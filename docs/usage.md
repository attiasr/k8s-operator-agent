---
abstract: This is the k8s operator agent usage guide.
authors: Rudy Attias, Steve Moore, Xander Harris
title: K8s Operator Agent Usage
---

## Path of minimum time sailed

This is going to be to install Docker Desktop, enable its internal Kubernetes
cluster then deploy the agent with skaffold and helm. The remainder of
this guide will assume that Docker Desktop has been deployed with the
required configuration and that helm and skaffold are available on the
user's system

### Helpful aliases

For the sake of saving keystrokes, you may find it helpful to alias helm to
'h' and kubectl to 'k'.

This can be done by updating your `.bashrc` with the following lines.

```{code-block} shell
alias h='helm'
alias k='kubectl'
```

If you'd like completion for these aliases, you can run the following commands.

```{code-block} shell
kubectl completion bash > /usr/local/share/bash-completion/completions/kubectl
kubectl completion bash > /usr/local/share/bash-completion/completions/k

helm completion bash > /usr/local/share/bash-completion/completions/helm
helm completion bash > /usr/local/share/bash-completion/completions/h
```

For the single-character files, you might find it convenient to copy
the completions from these locations, [h](path:/_static/completions/h) and
[k](path:/_static/completions/k)

### Provisioning for Development

If you happen to be on an underpowered workstation, you may consider using
[this Terraform code](https://github.com/edwardtheharris/tf-gcp-compute-instance)
to deploy a Google Compute Instance with the required resources for building
and running the project.

The default configuration of this project is much more powerful than
is required to do development on this project and costs almost nothing to run
provided that you only run it while you're using it.

## Skaffold

The quickest way to get up and running for the purpose of development is to
use the 'dev' command.

```{code-block} shell
skaffold dev
```

This will build and run the project for you in the configured Kubernetes
cluster then watch for code updates and refresh the running pods for you
while you're developing.
