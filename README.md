# Cold Email Generator

Cold Email Generator is a Python-based project that leverages AI and language models to automatically generate professional cold emails tailored for outreach, marketing, and business communication. It integrates Groq's large language models with LangChain to provide scalable, efficient, and customizable email generation.

## Features

- **AI-Powered Generation**: Uses Groq's LLMs with LangChain integration to generate relevant and professional cold emails.
- **Customizable Prompts**: Define input prompts such as target audience, tone, and purpose to create tailored emails.
- **Reusable Workflow**: Modular design allows easy extension for other use-cases like cover letters, LinkedIn messages, or proposals.
- **Scalable**: Built with production-ready libraries for reliable deployment.

## Tech Stack

- **Python 3.x**
- **LangChain** (for chaining LLM workflows)
- **Groq API** (for high-performance language generation)
- **Virtual Environment** (recommended for dependency isolation)

## Project Structure

```
Cold_email/
│── email_generator.py   # Main script to run email generation
│── requirements.txt     # Dependencies
│── README.md            # Project documentation
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cold-email-generator.git
   cd cold-email-generator
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv email
   email\Scripts\activate   # On Windows
   source email/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script to generate emails:

```bash
python email_generator.py
```

You can modify prompts inside the script to target different audiences or change tone/style.

## Contributing

Contributions are welcome! Feel free to fork the repository, create a new branch, and submit a pull request with improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
