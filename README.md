# Crypto projects 2023 (EPITA)

## Description
E-voting using homomorphic encryption or secure multiparty computation

## Repository Structure

```
│
├── data/
├── report/
├── slides/
├── src/
├── README.md
└── .gitignore
```

data: This folder contains the list of candidates and hashed credentials.
report: This folder contains generated reports in PDF format, along with their source files.
slides: This folder contains generated slides in PDF format, along with their source files.
src: This folder contains the source code files.
README.md: This file provides an overview of the project and the repository structure.
.gitignore: This file specifies the files and folders that should not be tracked by Git.

## Usage
### Requirement
```
cd src/
pip install -r requirement.txt
```

### Run a program
While in the "src" folder, start the server:
```
python3 server.py
```

Then run the client:
```
python3 client.py
```

### Modification

The program is highly modulable.
client.py will execute all the commands located in the __main__ function. Modify it at your desire to changes votes or make tests.
You can also decide to add more candidates in the "data/candidates.txt" file.
If you want to manually add credentials to "hashed\_credentials.txt", you can use the function hash.py to print the line to paste in the file.

## Keywords
- Homomorphic
- AES
- RSA
- CKKS
- Hash
- Salt
- E-Voting

