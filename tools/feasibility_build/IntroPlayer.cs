using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;

internal static class IntroPlayer
{
    [STAThread]
    private static int Main(string[] args)
    {
        if (args.Length < 1 || !File.Exists(args[0]))
            return 2;

        var mediaPath = Path.GetFullPath(args[0]);
        var app = new Application();

        var window = new Window
        {
            Title = "FM2001 Intro",
            WindowStyle = WindowStyle.None,
            WindowState = WindowState.Maximized,
            ResizeMode = ResizeMode.NoResize,
            Background = Brushes.Black,
            Topmost = true,
            ShowInTaskbar = false,
            Focusable = true,
        };

        var media = new MediaElement
        {
            Source = new Uri(mediaPath, UriKind.Absolute),
            LoadedBehavior = MediaState.Manual,
            UnloadedBehavior = MediaState.Manual,
            Stretch = Stretch.Uniform,
            ScrubbingEnabled = true,
        };

        bool failed = false;

        media.MediaOpened += (_, __) => media.Play();
        media.MediaEnded += (_, __) => window.Close();
        media.MediaFailed += (_, __) =>
        {
            failed = true;
            window.Close();
        };

        window.KeyDown += (_, e) =>
        {
            if (e.Key == Key.Escape || e.Key == Key.Space || e.Key == Key.Enter)
                window.Close();
        };

        window.MouseLeftButtonDown += (_, __) => window.Close();
        window.Content = media;
        window.Loaded += (_, __) =>
        {
            window.Activate();
            window.Focus();
            media.Play();
        };

        app.Run(window);
        return failed ? 3 : 0;
    }
}
