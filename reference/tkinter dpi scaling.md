# Can DPI scaling be enabled/disabled programmatically on a per-session basis?

From: <https://stackoverflow.com/questions/44398075/can-dpi-scaling-be-enabled-disabled-programmatically-on-a-per-session-basis>

Here's the answer I was looking for, based on comments by IInspectable and andlabs (many thanks):

```python
import ctypes

# Query DPI Awareness (Windows 10 and 8)
awareness = ctypes.c_int()
errorCode = ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness))
print(awareness.value)

# Set DPI Awareness  (Windows 10 and 8)
errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(2)
# the argument is the awareness level, which can be 0, 1 or 2:
# for 1-to-1 pixel control I seem to need it to be non-zero (I'm using level 2)

# Set DPI Awareness  (Windows 7 and Vista)
success = ctypes.windll.user32.SetProcessDPIAware()
# behaviour on later OSes is undefined, although when I run it on my Windows 10 machine, it seems to work with effects identical to SetProcessDpiAwareness(1)
```

The awareness levels are defined as follows:

```c
typedef enum _PROCESS_DPI_AWARENESS { 
    PROCESS_DPI_UNAWARE = 0,
    /*  DPI unaware. This app does not scale for DPI changes and is
        always assumed to have a scale factor of 100% (96 DPI). It
        will be automatically scaled by the system on any other DPI
        setting. */

    PROCESS_SYSTEM_DPI_AWARE = 1,
    /*  System DPI aware. This app does not scale for DPI changes.
        It will query for the DPI once and use that value for the
        lifetime of the app. If the DPI changes, the app will not
        adjust to the new DPI value. It will be automatically scaled
        up or down by the system when the DPI changes from the system
        value. */

    PROCESS_PER_MONITOR_DPI_AWARE = 2
    /*  Per monitor DPI aware. This app checks for the DPI when it is
        created and adjusts the scale factor whenever the DPI changes.
        These applications are not automatically scaled by the system. */
} PROCESS_DPI_AWARENESS;
```

Level 2 sounds most appropriate for my goal although 1 will also work provided there's no change in system resolution / DPI scaling.

SetProcessDpiAwareness will fail with errorCode = -2147024891 = 0x80070005 = E_ACCESSDENIED if it has previously been called for the current process (and that includes being called by the system when the process is launched, due to a registry key or .manifest file)
