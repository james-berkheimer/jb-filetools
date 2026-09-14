from filetools.settings import AppConfig

# Global settings instance (loaded once). Honours FILETOOLS_SETTINGS, falling back
# to the settings.json shipped with the package.
CONFIG = AppConfig()
