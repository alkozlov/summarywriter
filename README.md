# summarywriter

## CLI commands

### Install dependencies

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

### Run the application
To start the application, use the following command:

```bash
python main.py --file C:\Users\AKazlou\Downloads\OReilly_Certified_Kubernetes_Application_Developer_CKAD_Study_Gu.pdf --pages 43-58 --out output/
```

```bash
python main.py --query "Summarize the content of the PDF file 'C:\Users\AKazlou\Downloads\OReilly_Certified_Kubernetes_Application_Developer_CKAD_Study_Gu.pdf' from pages 43-58 and output to 'C:\Education\ai\summarywriter\output\summary-[START_PAGE]-[END_PAGE]_[TIMESTAMP].md'. [TIMESTAMP] is the current timestamp in the format YYYYMMDD_HHMMSS."
```

```bash
python main.py --query "Summarize the content of the PDF file 'C:\Users\AKazlou\Downloads\OReilly_Certified_Kubernetes_Application_Developer_CKAD_Study_Gu.pdf' for Chapter 5 'Pods and Namespaces'. Then output the result to file 'C:\Education\ai\summarywriter\output\summary_[TIMESTAMP].md' where [TIMESTAMP] is the current timestamp in the format YYYYMMDD_HHMMSS."
```