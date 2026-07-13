from config.env import env_bool, env_int, env_str


def init_sentry(*, debug: bool) -> None:
    """Initialize Sentry when SENTRY_DSN is configured."""
    dsn = env_str('SENTRY_DSN')
    if not dsn:
        return

    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    traces_sample_rate = env_int('SENTRY_TRACES_SAMPLE_RATE', default=10) / 100

    sentry_sdk.init(
        dsn=dsn,
        integrations=[DjangoIntegration()],
        traces_sample_rate=traces_sample_rate,
        send_default_pii=False,
        environment=env_str(
            'SENTRY_ENVIRONMENT',
            default='development' if debug else 'production',
        ),
    )
