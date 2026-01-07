from . import models


def post_init_hook(env):
    env['res.company']._set_addon_settings()
    env['res.config.settings']._set_config_settings()
