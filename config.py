from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="PYRA",
    settings_files=[
        "settings.toml",
        ".secrets.toml",
    ],
)
