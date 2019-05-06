TEMPLATE_HOME = {
    "@context": {
        "label": "http://www.w3.org/2000/01/rdf-schema#label",
        "hasRoom": "http://www.kadjanderman.com/ontology/property/hasRoom",
        "containsDevice": "http://www.kadjanderman.com/ontology/property/containsDevice"
    },
    "@type": "http://www.kadjanderman.com/ontology/class/Home",
}

TEMPLATE_ROOM = {
    "@context": {
        "label": "http://www.w3.org/2000/01/rdf-schema#label",
        "containsDevice": "http://www.kadjanderman.com/ontology/property/containsDevice",
        "partOf": "http://purl.org/dc/terms/isPartOf"
    },
    "@type": "http://www.kadjanderman.com/ontology/class/Room"
}

TEMPLATE_FOI = {
    "@context": {
        "label": "http://www.w3.org/2000/01/rdf-schema#label",
        "hasProperty": "http://www.kadjanderman.com/ontology/property/hasProperty",
        "featureOfInterestOf": "http://www.kadjanderman.com/ontology/property/featureOfInterestOf"
    },
    "@type": "http://www.kadjanderman.com/ontology/class/FeatureOfInterest"
}

TEMPLATE_DEVICE = {
    "@context": {
        "label": "http://www.w3.org/2000/01/rdf-schema#label",
        "actuates": "http://www.kadjanderman.com/ontology/property/actuates",
        "observes": "http://www.kadjanderman.com/ontology/property/observes",
    },
    "@type": "http://www.kadjanderman.com/ontology/class/Device"
}

TEMPLATE_PROPERTY = {
    "@context": {
        "label": "http://www.w3.org/2000/01/rdf-schema#label",
        "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#value",
        "last_updated": "http://www.kadjanderman.com/ontology/property/last_updated",
        "last_changed": "http://www.kadjanderman.com/ontology/property/last_changed"
    },
    "@type": "http://www.kadjanderman.com/ontology/class/Property"
}