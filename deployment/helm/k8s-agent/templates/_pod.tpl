
{{- define "k8s-agent.fileVolumes" -}}
  {{- if or .Values.global.files .Values.files }}
name: {{ include "k8s-agent.fullname" . }}
projected:
  sources:
  - secret:
      name: {{ include "k8s-agent.fullname" . }}
  {{- end }}
{{- end }}


{{- define "k8s-agent.pod" -}}
{{- $containers := (concat (list (include "k8s-agent.container" .| fromYaml)) .Values.extraContainers) -}}
{{- $volumes := compact (concat (list (include "k8s-agent.fileVolumes" . | fromYaml)) .Values.global.volumes .Values.volumes) -}}
metadata:
  annotations:
    checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
  {{- with (coalesce .Values.annotations .Values.global.annotations) }}
    {{- toYaml . | nindent 4 }}
  {{- end }}
  labels:
    {{- include "k8s-agent.labels" . | nindent 4 }}
spec:
  containers:
    {{- toYaml $containers | nindent 2 -}}

  {{- with $volumes }}
  volumes:
    {{- toYaml $volumes | nindent 2 }}
  {{- end }}

  {{- with (coalesce .Values.imagePullSecrets .Values.global.imagePullSecrets) }}
  imagePullSecrets:
    {{- toYaml . | nindent 2 }}
  {{- end }}

  {{- with (coalesce .Values.ndots .Values.global.ndots) }}
  dnsConfig:
    options:
      - name: ndots
        value: {{ . | quote }}
  {{- end }}

  {{- with (coalesce .Values.podSecurityContext .Values.global.podSecurityContext) }}
  securityContext:
    {{- toYaml . | nindent 4 }}
  {{- end }}

  {{- with (coalesce .Values.nodeSelector .Values.global.nodeSelector) }}
  nodeSelector:
    {{- toYaml . | nindent 4 }}
  {{- end }}

  {{- if or .Values.topologySpreadConstraints .Values.global.topologySpreadConstraints }}
  topologySpreadConstraints:
    {{- toYaml (default .Values.global.topologySpreadConstraints .Values.topologySpreadConstraints) | nindent 4 }}
  {{- else if .Values.defaultTopologyConstrains }}
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          {{ include "http-service.selectorLabels" . | nindent 6 }}
      matchLabelKeys:
        - pod-template-hash
      nodeAffinityPolicy: Honor
      nodeTaintsPolicy: Honor
    - maxSkew: 1
      topologyKey: kubernetes.io/hostname
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          {{ include "http-service.selectorLabels" . | nindent 6 }}
      matchLabelKeys:
        - pod-template-hash
      nodeAffinityPolicy: Honor
      nodeTaintsPolicy: Honor
  {{- end }}

  {{- if or .Values.affinity .Values.global.affinity }}
  affinity:
    {{- with (coalesce .Values.affinity.nodeAffinity .Values.global.affinity.nodeAffinity) }}
    nodeAffinity:
      {{- toYaml . | nindent 6 }}
    {{- end }}
    {{- with (coalesce .Values.affinity.nodeAntiAffinity .Values.global.affinity.nodeAntiAffinity) }}
    nodeAntiAffinity:
      {{- toYaml . | nindent 6 }}
    {{- end }}
    {{- with (coalesce .Values.affinity.podAffinity .Values.global.affinity.podAffinity) }}
    podAffinity:
      {{- toYaml . | nindent 6 }}
    {{- end }}
    {{- with (coalesce .Values.affinity.podAntiAffinity .Values.global.affinity.podAntiAffinity) }}
    podAntiAffinity:
      {{- toYaml . | nindent 6 }}
    {{- end }}
  {{- end }}

  {{- with (coalesce .Values.tolerations .Values.global.tolerations) }}
  tolerations:
    {{- toYaml . | nindent 4 }}
  {{- end }}

  {{- if .Values.dnsPolicy }}
  dnsPolicy: {{ .Values.dnsPolicy }}
  {{- end }}

  {{- if .Values.restartPolicy }}
  restartPolicy: {{ .Values.restartPolicy }}
  {{- end }}
  terminationGracePeriodSeconds: {{ default 5 .Values.terminationGracePeriodSeconds }}
  serviceAccountName: {{ template "k8s-agent.serviceAccountName" . }}
{{- end }}
