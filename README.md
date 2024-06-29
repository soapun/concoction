# Concoction

Concoction is a simple configuration injection library that allows you to easily inject configuration values into your
Python applications. It supports both `pydantic` and `dataclasses` for defining configuration models. Unlike traditional
configuration management tools, Concoction does not parse or layer configurations; it only works with a dictionary
object as an input.

## Inspiration

Concoction is inspired by the `@ConfigurationProperties` and `@Value` annotations from Spring Boot. These annotations
allow for easy injection of configuration properties into Java applications, and Concoction aims to provide a similar
experience for Python developers.

## Key Features

- **Flexibility with Plain Dictionaries**: Simple and flexible configuration management using plain dictionaries.
- **Injecting Whole Configuration Blocks**: Inject entire configuration blocks for modular and decoupled settings.
- **Injecting Individual Fields**: Granular control with the ability to inject specific configuration fields.

## Installation

To install Concoction, run the following command:

```bash
pip install concoction
```

## Usage

Here is an example of `config.yaml` file:

```yaml
app:
  service:
    host: 0.0.0.0
    port: 8000
```

and injecting `service` section into our config

```python
import yaml  # pip install pyyaml
from pydantic import BaseModel
from concoction import Configuration, set_global_config


# define config with injection

@Configuration("app.service")
class ServiceConfig(BaseModel):
    host: str
    port: int


# Load configuration from a YAML file
with open("config.yaml") as f:
    config = yaml.safe_load(f)

set_global_config(config)

# Create an instance of the configuration model
app_config = ServiceConfig()
```

or field-wise

```python
from concoction.values.pydantic import Value


class ServiceConfig(BaseModel):
    host: str = Value("app.service.host")
    port: int = Value("app.service.port")
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.