---
abstract: This document describes the architecture of the k8s operator agent.
authors: Rudy Attias, Steve Moore, Xander Harris
title: K8s Operator Agent Architecture
---

1. Generate a prompt by injecting user defined variables.
2. Call the GPT API with the prompt.
3. We'll parse the output.
   1. The output of the LLM needs to be available in several formats, for
        instance JSON.
   2. To do this we'll use Pydantic.
