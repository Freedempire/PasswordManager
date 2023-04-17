# How to correctly set PYTHONPATH for Visual Studio Code

From: <https://stackoverflow.com/questions/53653083/how-to-correctly-set-pythonpath-for-visual-studio-code>

## Answer

Suppose your project layout is like this:

```txt
myproject/
├── .env
├── .vscode/
|   └── settings.json
├── src/
|   └── a_module.py
└── tests/
    └── test_a.py
```

Open the settings.json file and insert these lines

```txt
"terminal.integrated.env.windows": {
    "PYTHONPATH": "${workspaceFolder}/src;${workspaceFolder}/tests"
},
"python.envFile": "${workspaceFolder}/.env",
```

Note that `${workspaceFolder}` evaluates to `myproject`, it is not to the .vscode folder.

In the .env file enter this

```txt
WORKSPACE_FOLDER=C:/full/path/to/myproject
PYTHONPATH=${WORKSPACE_FOLDER}/src;${WORKSPACE_FOLDER}/tests
```

Note that on Windows the slashes in the path lean forward, like so `/`. Different paths are separated with a `;` (on other platforms with a `:`).

## Comment to the answer

The default location assumed for .env file is the root of your workspace, so you only need to use settings.json to specify a different location.

Environment variables defined in .env accept relative paths, so in the example above `PYTHONPATH=src;tests` is sufficient. Not only is there no need to define `WORKSPACE_FOLDER`, but doing so also makes the .env file non-transferrable (e.g. including it in git will likely cause issues across users).

## Official doc from VS Code

From: <https://code.visualstudio.com/docs/python/environments#_use-of-the-pythonpath-variable>

> Use of the `PYTHONPATH` variable
>
> The `PYTHONPATH` environment variable specifies additional locations where the Python interpreter should look for modules. In VS Code, `PYTHONPATH` can be set through the terminal settings (`terminal.integrated.env.*`) and/or within an .env file.
>
> When the terminal settings are used, `PYTHONPATH` affects any tools that are run within the terminal by a user, as well as any action the extension performs for a user that is routed through the terminal such as debugging. However, in this case when the extension is performing an action that isn't routed through the terminal, such as the use of a linter or formatter, then this setting won't have an effect on module look-up.

## Conclusion

The .env file is not necessary, and in settings.json file, there's no need to include `${workspaceFolder}/` in the path for `"PYTHONPATH"`.
