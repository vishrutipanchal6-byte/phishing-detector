class FeatureExtraction:
    def __init__(self, url):
        self.url = url

    def getFeaturesList(self):
        features = []

        # URL length
        features.append(len(self.url))

        # HTTPS check
        if "https" in self.url:
            features.append(1)
        else:
            features.append(0)

        return features