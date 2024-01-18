{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "k8s-agent.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "k8s-agent.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "k8s-agent.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "k8s-agent.labels" -}}
{{- $labels := deepCopy .Values.labels | mergeOverwrite (deepCopy .Values.global.labels) -}}
helm.sh/chart: {{ include "k8s-agent.chart" . }}
app.kubernetes.io/name: {{ include "k8s-agent.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
  {{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
  {{- end }}
  {{- if $labels }}
{{ toYaml $labels }}
  {{- end }}
  {{- if .Values.selectorLabels }}
{{- toYaml .Values.selectorLabels }}
  {{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "k8s-agent.selectorLabels" -}}
  {{- if .Values.selectorLabels }}
{{- toYaml .Values.selectorLabels }}
  {{- else }}
app.kubernetes.io/name: {{ include "k8s-agent.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
  {{- end }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "k8s-agent.serviceAccountName" -}}
{{- if or (.Values.serviceAccount.create) (.Values.global.serviceAccount.create) -}}
    {{ default (include "k8s-agent.fullname" .) (coalesce .Values.serviceAccount.name .Values.global.serviceAccount.name) }}
{{- else -}}
    {{ default "default" (coalesce .Values.serviceAccount.name .Values.global.serviceAccount.name) }}
{{- end -}}
{{- end -}}

{{- define "k8s-agent.secretFilesName" -}}
{{ include "k8s-agent.fullname" . | trunc 50 | trimSuffix "-" }}-secret-files
{{- end -}}


{{- define "k8s-agent.image" -}}
  {{- if typeIs "string" .Values.global.image -}}
{{- required ".Values.global.image is required!" .Values.global.image }}
  {{- else if typeIs "string" .Values.image -}}
{{- required ".Values.image is required!" .Values.image }}
  {{- else -}}
{{- $imageRepo := ( required ".Values.image.repository must be set" (coalesce .Values.image.repository .Values.global.image.repository)) }}
{{- $imageTag := ( default "latest" (coalesce .Values.image.tag .Values.global.image.tag)) }}
{{- $imageRegistry := (coalesce .Values.image.registry .Values.global.image.registry) }}
{{- if $imageRegistry -}}{{ $imageRegistry }}/{{- end -}}{{$imageRepo}}:{{$imageTag}}
  {{- end -}}
{{- end -}}
