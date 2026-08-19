variable "project_name" {
  type        = string
  description = "Nome do projeto (usado como prefixo)"
}

variable "function_name" {
  type        = string
  description = "Identificador da função Lambda (sem prefixo)"
}

variable "environment" {
  type        = string
  description = "Ambiente de deploy (dev, staging, prod)"
}

variable "description" {
  type        = string
  description = "Descrição da função Lambda"
  default     = ""
}

variable "handler" {
  type        = string
  description = "Handler da Lambda (módulo.função)"
  default     = "handler.handler"
}

variable "timeout" {
  type        = number
  description = "Timeout em segundos"
  default     = 30
}

variable "memory_size" {
  type        = number
  description = "Memória em MB"
  default     = 256
}

variable "source_path" {
  type        = string
  description = "Caminho para o código fonte (não usado — mantido para compatibilidade)"
  default     = ""
}

variable "package_path" {
  type        = string
  description = "Caminho para o zip pré-construído da Lambda"
}

variable "environment_variables" {
  type        = map(string)
  description = "Variáveis de ambiente para a Lambda"
  default     = {}
}

variable "policy_statements" {
  type        = any
  description = "Statements de IAM policy a anexar ao execution role"
  default     = {}
}
