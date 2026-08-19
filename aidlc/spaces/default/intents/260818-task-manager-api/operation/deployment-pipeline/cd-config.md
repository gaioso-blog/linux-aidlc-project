# CD Configuration — Task Manager API
<!-- confirmed -->

## Upstream Artifacts

- `construction/ci-pipeline/ci-config.md` — GitHub Actions CI (ci.yml já implementado)
- `construction/ci-pipeline/quality-gates.md` — gates blocking

## Arquivo de Deploy

Criar `.github/workflows/deploy.yml` após o primeiro `terraform apply` manual bem-sucedido (que gera o CloudFront Distribution ID necessário):

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    name: Deploy to AWS
    runs-on: ubuntu-latest
    needs: []  # Adicionar: needs: [test] se ci.yml e deploy.yml forem mesclados
    environment: production  # GitHub Environment com aprovação manual opcional
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.13
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"
          cache: "pip"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "~> 1.6"

      - name: Terraform Init
        run: |
          terraform init \
            -backend-config="bucket=${{ secrets.TF_STATE_BUCKET }}" \
            -backend-config="key=${{ secrets.TF_STATE_KEY }}" \
            -backend-config="region=us-east-1"
        working-directory: infra/environments/dev

      - name: Terraform Plan
        run: terraform plan -out=tfplan
        working-directory: infra/environments/dev

      - name: Terraform Apply
        run: terraform apply -auto-approve tfplan
        working-directory: infra/environments/dev

      - name: Deploy frontend to S3
        run: |
          BUCKET=$(terraform output -raw frontend_bucket_name)
          aws s3 sync frontend/ s3://$BUCKET/ --delete
        working-directory: infra/environments/dev

      - name: Invalidate CloudFront cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"

      - name: Smoke test
        run: |
          API_URL=$(cd infra/environments/dev && terraform output -raw api_gateway_url)
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/v1/tasks")
          echo "API status: $STATUS"
          # 401 is expected (no auth token) — confirms API is up
          if [ "$STATUS" != "401" ] && [ "$STATUS" != "200" ]; then
            echo "Smoke test failed: unexpected status $STATUS"
            exit 1
          fi
          echo "Smoke test passed"
```

## Outputs Terraform Necessários

Adicionar a `infra/environments/dev/outputs.tf`:

```hcl
output "api_gateway_url" {
  value = module.api_gateway.invoke_url
}

output "frontend_bucket_name" {
  value = module.frontend.s3_bucket_name
}

output "cloudfront_domain" {
  value = module.frontend.cloudfront_domain_name
}
```

## Primeiro Deploy (Manual)

O primeiro deploy deve ser feito manualmente para:
1. Capturar o `CLOUDFRONT_DISTRIBUTION_ID` para configurar o GitHub Secret
2. Verificar que todos os módulos Terraform aplicam sem erros
3. Configurar os GitHub Secrets antes de ativar o CD automático

```bash
cd infra/environments/dev
terraform init -backend-config="bucket=SEU-BUCKET" -backend-config="key=task-manager/dev/terraform.tfstate" -backend-config="region=us-east-1"
terraform plan
terraform apply
```
