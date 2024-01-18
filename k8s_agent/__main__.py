import kopf

@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, logger, **_):
    print(settings)


@kopf.index('', 'v1', 'pod')
def my_handler(name, body, **kwargs):
    print(name)


if __name__ == '__main__':
    kopf.run(clusterwide=True)
