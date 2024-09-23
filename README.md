<div align="center">

  <h1>DARC</h1>
  <i>Decentralized Agent Relay for Communication and Engagement</i>
  
  <p>
    <!-- An awesome README template for your projects!  -->
  </p>
  <img src="assets/logo.png" alt="logo" width="800" height="auto" />
  
<!-- Badges -->
<p>
<img src="https://img.shields.io/badge/python-3.10-yellow"/>
<img src="https://img.shields.io/badge/elixir-1.17.2-purple"/>
<img src="https://img.shields.io/badge/erlang/OTC-16.1-red"/>
  <a href="#">
    <img src="https://img.shields.io/badge/license-undo-white"/>
  </a>
</p>
   
<h6>
    <a href="#">View Demo</a>
  <span> · </span>
    <a href="#">Documentation</a>
</h6>
</div>

<br />

<!-- Table of Contents -->
# Table of Contents

<!-- - [Table of Contents](#table-of-contents)
  - [About the Project](#about-the-project)
    - [Screenshots](#screenshots)
    - [Tech Stack](#tech-stack)
    - [Features](#features)
    - [Color Reference](#color-reference)
    - [Environment Variables](#environment-variables)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Running Tests](#running-tests)
    - [Run Locally](#run-locally)
    - [Deployment](#deployment)
  - [Usage](#usage)
  - [Roadmap](#roadmap)
  - [Contributing](#contributing)
    - [Code of Conduct](#code-of-conduct)
  - [FAQ](#faq)
  - [License](#license)
  - [Contact](#contact)
  - [Acknowledgements](#acknowledgements) -->
- [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Installation \& Config](#installation--config)
    - [Source Code](#source-code)
    - [Docker](#docker)
  - [Quick Start](#quick-start)
  - [Optional Usage](#optional-usage)
  - [Roadmap](#roadmap)
  - [Contact](#contact)

## Introduction
When you need a large-scale multi-agents, try this.

## Installation & Config
### Source Code
1. Install [conda](https://docs.conda.io/en/latest/miniconda.html) if you want to keep your environment clean. 
Then create a conda environment.

```bash
conda create -n darc python=3.10
conda activate your_env_name
```
2. Install [poetry](https://python-poetry.org/docs/#installation)

```bash
poetry install && make compile
```

3. Install [postgre](https://www.postgresql.org/download/)

4. Install [Erlang](https://www.erlang.org/downloads) & [Elixir](https://elixir-lang.org/install.html) according to your OS.

- Erlang/OTP 26
- Elixir 1.17.2

4. Install the Erlang/Elixir packages

```bash
cd darc/ain
mix do deps.get, deps.compile
```

5. Config
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

### Docker
**Note**: Fill in your OPENAI_API_KEY in ./docker-compose.yml
```bash
   docker-compose up --build
```

## Quick Start
A chat example
```python
postgre_url = "your_postgre_url"
with MAS("postgre_url") as mas:
  mas.clear_tables()
  chat_config = {
    "role": [
      "People",
    ],
    "edge": [
      ("People", "People"),
    ],
    "args": [
      ("People", 4),
    ]
  }

  mas.config_db(chat_config)

  # The generation of multiple agents takes time
  time.sleep(32)
  actors = mas.find_with_role("People")
  mas.bind_system_prompt(actors)
  
  mas.send(str(actors[0].uid), content)

  # Let the multi-agent discuss for a while
  time.sleep(256)
  any_actor = actors[random.randint(0, len(actors) - 1)]
  logs = mas.get_log(str(any_actor.uid))
```

## Optional Usage
- Customize the agent
- 

<!-- Color Reference -->
<!-- ### Color Reference

| Color             | Hex                                                                |
| ----------------- | ------------------------------------------------------------------ |
| Primary Color | ![#222831](https://via.placeholder.com/10/222831?text=+) #222831 |
| Secondary Color | ![#393E46](https://via.placeholder.com/10/393E46?text=+) #393E46 |
| Accent Color | ![#00ADB5](https://via.placeholder.com/10/00ADB5?text=+) #00ADB5 |
| Text Color | ![#EEEEEE](https://via.placeholder.com/10/EEEEEE?text=+) #EEEEEE |
 -->

<!-- Roadmap -->
## Roadmap

* [ ] Docker configuration


<!-- Contributing -->
<!-- ## Contributing

<a href="https://github.com/Louis3797/awesome-readme-template/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Louis3797/awesome-readme-template" />
</a>


Contributions are always welcome!

See `contributing.md` for ways to get started. -->



<!-- License -->
<!-- ## License

Distributed under the no License. See LICENSE.txt for more information. -->


<!-- Contact -->
## Contact
Any questions or feedback with DARC, please contact us.
- Email: sys555@outlook.com
- GitHub Issues: [DARC](https://github.com/sys555/darc/issues)
