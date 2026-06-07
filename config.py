import yaml

DEFAULT_CONFIG = {
    "locationUpdateInterval": 0.5,
    "minLocationDistance": 1.0,
    "randomizeRoute": False,
    "cacheRoute": True,
    "speedVariation": 0.0,
    "lowPriority": True,
}

class Config:
    def __init__(self, values=None):
        if values is None:
            with open("config.yaml", 'r') as f:
                values = yaml.safe_load(f)
        values = {**DEFAULT_CONFIG, **(values or {})}
        for i in values:
            setattr(self, i, values[i])


config = Config()
