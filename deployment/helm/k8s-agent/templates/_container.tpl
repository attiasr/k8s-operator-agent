{{- define "k8s-agent.container" -}}
  {{- $root := . -}}
  {{- $envVars := deepCopy .Values.envVars | mergeOverwrite (deepCopy .Values.global.envVars) -}}
name: {{ include "k8s-agent.fullname" . }}
  {{- with (coalesce .Values.securityContext .Values.global.securityContext) }}
securityContext:
  {{- toYaml . | nindent 2 }}
  {{- end }}
  {{- if .Values.command }}
command: ["{{ .Values.command }}"]
  {{- end }}
  {{- if .Values.args }}
args:
  {{- toYaml .Values.args | nindent 2 }}
  {{- end }}
image: "{{ include "k8s-agent.image" . }}"
  {{- if and (not (typeIs "string" .Values.global.image)) (not (typeIs "string" .Values.image)) }}
imagePullPolicy: {{ coalesce .Values.image.pullPolicy .Values.global.image.pullPolicy | default "IfNotPresent" }}
  {{- end }}
  {{- if .Values.ports }}
ports:
  {{- .Values.ports | toYaml | nindent 2 }}
  {{- end }}
env:
  - name: NODE_NAME
    valueFrom:
      fieldRef:
        fieldPath: spec.nodeName
  - name: POD_NAME
    valueFrom:
      fieldRef:
        fieldPath: metadata.name
  - name: POD_NAMESPACE
    valueFrom:
      fieldRef:
        fieldPath: metadata.namespace
  - name: POD_IP
    valueFrom:
      fieldRef:
        fieldPath: status.podIP
  - name: POD_SERVICE_ACCOUNT
    valueFrom:
      fieldRef:
        fieldPath: spec.serviceAccountName
  {{- if $envVars }}
    {{- range $key, $val := $envVars }}
      {{- if $val }}
  - name: {{ $key | quote }}
    valueFrom:
      secretKeyRef:
        name: {{ include "k8s-agent.fullname" $root }}
        key: {{ $key | quote }}
      {{- end }}
    {{- end }}
  {{- end }}
volumeMounts:
  {{- if or .Values.global.files .Values.files }}
    {{- $filesPaths := keys .Values.files .Values.global.files | uniq | sortAlpha }}
    {{- $root := . -}}
    {{- range $path := $filesPaths }}
  - name: {{ include "k8s-agent.fullname" $root }}
    mountPath: {{ $path }}
    subPath: {{ trimPrefix "/" $path | replace "/" "-" | replace "." "-" | quote }}
    readOnly: true
    {{- end }}
  {{- else }}
  []
  {{- end }}
  {{- if .Values.livenessProbe }}
livenessProbe:
  {{- .Values.livenessProbe | toYaml | nindent 2 }}
  {{- end }}
  {{- if .Values.readinessProbe }}
readinessProbe:
  {{- .Values.readinessProbe | toYaml | nindent 2 }}
  {{- end }}
  {{- with (coalesce .Values.resources .Values.global.resources ) }}
resources:
  {{- toYaml . | nindent 2 }}
  {{- end }}
  {{- with .Values.lifecycle }}
lifecycle:
  {{- toYaml . | nindent 2 }}
  {{- end }}
{{- end }}
