---
abstract: >
    This document requires the tooling required for the k8s operator agent.
authors: Rudy Attias, Steve Moore, Xander Harris
title: K8s Operator Agent Tooling
---

## Python

This project uses Python.

## FastAPI

Allows simple, trivial access to custom APIs.

## LangServe

[LangServe](https://www.langchain.com/langserve) is part of the
[LangChain](https://www.langchain.com/) set of services.

LangChain provides context management for LLM interactions. For the
purposes of this project, the relevant portion of the LangChang
documentation is its
[Python](https://python.langchain.com/docs/get_started/introduction)
implementation

## CI/CD

This is handled with GitHub Actions.

```{autoyaml} .github/workflows/docs.yml
```
