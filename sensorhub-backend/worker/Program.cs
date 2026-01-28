using System.Buffers.Binary;
using System.Text.Json;
using System.Threading;
using Windows.Devices.Enumeration;
using Windows.Graphics.Imaging;
using Windows.Media.Capture;
using Windows.Media.Capture.Frames;
using Windows.Media.MediaProperties;
using Windows.Storage.Streams;

namespace CameraWorker;

internal static class Program
{
    private const string Magic = "FRAM";
    private const ushort Version = 1;
    public static int Main(string[] args)
    {
        try
        {
            return Run(args).GetAwaiter().GetResult();
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"worker fatal: {ex}");
            return 1;
        }
    }

    private static async Task<int> Run(string[] args)
    {
        var list = args.Contains("--list");
        var deviceId = GetArgValue(args, "--device");

        if (list)
        {
            await ListDevices();
            return 0;
        }

        if (string.IsNullOrWhiteSpace(deviceId))
        {
            Console.Error.WriteLine("Usage: camera_worker.exe --list | --device <symbolic_link>");
            return 2;
        }

        await StreamDevice(deviceId);
        return 0;
    }

    private static string? GetArgValue(string[] args, string key)
    {
        for (var i = 0; i < args.Length - 1; i++)
        {
            if (args[i] == key)
            {
                return args[i + 1];
            }
        }
        return null;
    }

    private static async Task ListDevices()
    {
        var properties = new[]
        {
            "System.ItemNameDisplay",
            "System.Devices.FriendlyName",
            "System.Devices.DeviceInstanceId",
            "System.Devices.LocationPaths"
        };
        var selector = DeviceInformation.GetAqsFilterFromDeviceClass(DeviceClass.VideoCapture);
        var devices = await DeviceInformation.FindAllAsync(selector, properties);
        var payload = devices.Select(d => new
        {
            device_id = d.Id,
            friendly_name = ResolveFriendlyName(d),
            port_id = ResolvePortId(d),
            instance_id = ResolveInstanceId(d)
        });
        var json = JsonSerializer.Serialize(payload);
        Console.Out.WriteLine(json);
    }

    private static string ResolveFriendlyName(DeviceInformation device)
    {
        if (device.Properties.TryGetValue("System.ItemNameDisplay", out var itemName) && itemName is string item)
        {
            return item;
        }
        if (device.Properties.TryGetValue("System.Devices.FriendlyName", out var friendly) && friendly is string friendlyName)
        {
            return friendlyName;
        }
        return device.Name;
    }

    private static string ResolvePortId(DeviceInformation device)
    {
        if (device.Properties.TryGetValue("System.Devices.LocationPaths", out var locations))
        {
            if (locations is string[] paths && paths.Length > 0)
            {
                return paths[0];
            }
            if (locations is IReadOnlyList<string> list && list.Count > 0)
            {
                return list[0];
            }
        }
        return "";
    }

    private static string ResolveInstanceId(DeviceInformation device)
    {
        if (device.Properties.TryGetValue("System.Devices.DeviceInstanceId", out var instance))
        {
            if (instance is string instanceId && !string.IsNullOrWhiteSpace(instanceId))
            {
                return instanceId;
            }
        }
        return "";
    }

    private static async Task StreamDevice(string deviceId)
    {
        var capture = new MediaCapture();
        var settings = new MediaCaptureInitializationSettings
        {
            VideoDeviceId = deviceId,
            StreamingCaptureMode = StreamingCaptureMode.Video,
            SharingMode = MediaCaptureSharingMode.SharedReadOnly,
            MemoryPreference = MediaCaptureMemoryPreference.Cpu
        };
        try
        {
            await capture.InitializeAsync(settings);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"init failed: {ex.Message}");
            return;
        }

        var source = capture.FrameSources.Values
            .FirstOrDefault(s => s.Info.SourceKind == MediaFrameSourceKind.Color);
        if (source == null)
        {
            Console.Error.WriteLine("no color source");
            return;
        }

        var reader = await capture.CreateFrameReaderAsync(source, MediaEncodingSubtypes.Bgra8);
        var semaphore = new SemaphoreSlim(1, 1);
        ulong sequence = 0;

        reader.FrameArrived += async (_, _) =>
        {
            if (!await semaphore.WaitAsync(0))
            {
                return;
            }
            try
            {
                using var frame = reader.TryAcquireLatestFrame();
                if (frame == null)
                {
                    return;
                }
                var bitmap = frame.VideoMediaFrame?.SoftwareBitmap;
                if (bitmap == null)
                {
                    return;
                }
                if (bitmap.BitmapPixelFormat != BitmapPixelFormat.Bgra8)
                {
                    bitmap = SoftwareBitmap.Convert(bitmap, BitmapPixelFormat.Bgra8);
                }
                var jpeg = await EncodeJpeg(bitmap);
                if (jpeg == null || jpeg.Length == 0)
                {
                    return;
                }
                WriteFrame(deviceId, "image/jpeg", sequence++, (ulong)DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(), jpeg);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"frame error: {ex.Message}");
            }
            finally
            {
                semaphore.Release();
            }
        };

        await reader.StartAsync();
        await Task.Delay(Timeout.Infinite);
    }

    private static async Task<byte[]?> EncodeJpeg(SoftwareBitmap bitmap)
    {
        using var stream = new InMemoryRandomAccessStream();
        var encoder = await BitmapEncoder.CreateAsync(BitmapEncoder.JpegEncoderId, stream);
        encoder.SetSoftwareBitmap(bitmap);
        await encoder.FlushAsync();

        var buffer = new byte[stream.Size];
        await stream.AsStream().ReadAsync(buffer, 0, buffer.Length);
        return buffer;
    }

    private static void WriteFrame(string deviceId, string mime, ulong sequence, ulong timestampMs, byte[] payload)
    {
        var deviceBytes = System.Text.Encoding.UTF8.GetBytes(deviceId);
        var mimeBytes = System.Text.Encoding.UTF8.GetBytes(mime);

        var headerLen = 4 + 2 + 2 + 8 + 8 + 2 + 2 + 4;
        Span<byte> header = stackalloc byte[headerLen];
        System.Text.Encoding.ASCII.GetBytes(Magic, header);
        BinaryPrimitives.WriteUInt16LittleEndian(header[4..6], Version);
        BinaryPrimitives.WriteUInt16LittleEndian(header[6..8], (ushort)headerLen);
        BinaryPrimitives.WriteUInt64LittleEndian(header[8..16], sequence);
        BinaryPrimitives.WriteUInt64LittleEndian(header[16..24], timestampMs);
        BinaryPrimitives.WriteUInt16LittleEndian(header[24..26], (ushort)deviceBytes.Length);
        BinaryPrimitives.WriteUInt16LittleEndian(header[26..28], (ushort)mimeBytes.Length);
        BinaryPrimitives.WriteUInt32LittleEndian(header[28..32], (uint)payload.Length);

        var output = Console.OpenStandardOutput();
        output.Write(header);
        output.Write(deviceBytes, 0, deviceBytes.Length);
        output.Write(mimeBytes, 0, mimeBytes.Length);
        output.Write(payload, 0, payload.Length);
        output.Flush();
    }
}
