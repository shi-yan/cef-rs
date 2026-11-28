# update-bindings

Download the prebuilt [Chromium Embedded Framework](https://github.com/chromiumembedded/cef)
archive on any supported platform and run `bindgen` on the C API for the `cef-dll-sys` crate,
then regenerate the safe bindings in the `cef` crate.

You can find the latest version of the prebuilt CEF archives on the [Chromium Embedded Framework
(CEF) Automated Builds](https://cef-builds.spotifycdn.com/index.html).

CEF 158 input utilities are included by `sys/wrapper.h`. The two scalar helpers
can also be synchronized across all checked-in targets from a Linux generation:

```sh
CEF_PATH_linux_x86_64=/path/to/cef-distribution \
  python3 update-bindings/sync_input_helpers.py /path/to/update-bindings
```

This runs bindgen against the real C API header (including its API-version guards),
checks the exact `uint32_t`/`int` signatures, propagates only the platform-independent
virtual-key helper and Linux-only keysym helper, and regenerates every safe wrapper.
It does not copy native-handle APIs between platforms. Full native generation also
includes the header for future updates. Set `BINDGEN_EXTRA_CLANG_ARGS` to the local
Clang resource directory when the host lacks Clang's standard builtin headers.
The generator formats only its output file, never the invoking workspace.
