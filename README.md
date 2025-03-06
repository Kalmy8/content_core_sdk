## Package Structure:

content-core-sdk/
├── content_core/ │
│    ├── kafka/
│    │   ├── __init__.py
│    │   ├── client.py      # KafkaService class
│    │   └── config.py      # KafkaConfig
│    ├── models/
│    │   ├── __init__.py
│    │   ├── base.py        # ISerializable
│    │   ├── enums.py        # KafkaTopics
│    │   ├── text_generation_models.py     # ContentRequestsText, ContentResponsesText
│    │   └── ...
│    
├── pyproject.toml
├── README.md
└── setup.cfg