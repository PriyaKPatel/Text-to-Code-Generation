# 🔐 GitHub Secrets Setup Guide

## Step-by-Step Instructions

### 1. Go to GitHub Secrets Page

Open this URL in your browser:
```
https://github.com/PriyaKPatel/Text-to-Code-Generation/settings/secrets/actions
```

---

### 2. Add Each Secret

Click **"New repository secret"** and add the following **8 secrets**:

---

#### **Secret 1: AWS_ACCOUNT_ID**
- **Name**: `AWS_ACCOUNT_ID`
- **Value**: `518627289438`

---

#### **Secret 2: AWS_ACCESS_KEY_ID**
- **Name**: `AWS_ACCESS_KEY_ID`
- **Value**: Get from one of these sources:
  
  **Option A: From AWS CLI credentials file**
  ```bash
  cat ~/.aws/credentials
  ```
  Look for: `aws_access_key_id = AKIA...`
  
  **Option B: From AWS Console**
  1. Go to: https://console.aws.amazon.com/iam/
  2. Click: Users → text-to-code-deploy → Security credentials
  3. Create new access key if needed

---

#### **Secret 3: AWS_SECRET_ACCESS_KEY**
- **Name**: `AWS_SECRET_ACCESS_KEY`
- **Value**: Get from the same source as AWS_ACCESS_KEY_ID
  
  From `~/.aws/credentials`:
  Look for: `aws_secret_access_key = ...`

---

#### **Secret 4: EC2_HOST**
- **Name**: `EC2_HOST`
- **Value**: `3.85.224.148`

---

#### **Secret 5: EC2_USERNAME**
- **Name**: `EC2_USERNAME`
- **Value**: `ubuntu`

---

#### **Secret 6: EC2_SSH_KEY**
- **Name**: `EC2_SSH_KEY`
- **Value**: Complete content of your SSH private key

  **Get the key:**
  ```bash
  cat ~/Downloads/text-to-code-key.pem
  ```
  
  **⚠️ Important**: Copy the ENTIRE content including:
  ```
  -----BEGIN RSA PRIVATE KEY-----
  MIIEpAIBAAKCAQEA...
  ...all lines...
  ...all lines...
  -----END RSA PRIVATE KEY-----
  ```

---

#### **Secret 7: S3_BUCKET**
- **Name**: `S3_BUCKET`
- **Value**: `text-to-code-models-priya`

---

#### **Secret 8: S3_PREFIX**
- **Name**: `S3_PREFIX`
- **Value**: `models/v1`

---

## 3. Verify Secrets Added

After adding all secrets, you should see **8 secrets** in the list:
- ✅ AWS_ACCOUNT_ID
- ✅ AWS_ACCESS_KEY_ID
- ✅ AWS_SECRET_ACCESS_KEY
- ✅ EC2_HOST
- ✅ EC2_USERNAME
- ✅ EC2_SSH_KEY
- ✅ S3_BUCKET
- ✅ S3_PREFIX

---

## 4. Test the CI/CD Pipeline

Once all secrets are added, the pipeline will trigger automatically on the next push to `main` branch.

**Manual trigger test:**
```bash
# Make a small change
echo "# CI/CD Test" >> README.md

# Commit and push
git add README.md
git commit -m "Test CI/CD pipeline"
git push origin main
```

**Monitor the workflow:**
1. Go to: https://github.com/PriyaKPatel/Text-to-Code-Generation/actions
2. Watch the workflow run (should complete in ~5-10 minutes)

---

## 5. What Happens Automatically

When you push to `main`, GitHub Actions will:

1. ✅ **Test**: Run pytest and linting
2. ✅ **Build**: Build Docker image
3. ✅ **Push**: Push to AWS ECR
4. ✅ **Deploy**: Deploy to EC2 automatically
5. ✅ **Verify**: Check health endpoint

---

## Troubleshooting

### If workflow fails:

1. **Check secrets are correct**:
   - Go to: https://github.com/PriyaKPatel/Text-to-Code-Generation/settings/secrets/actions
   - Verify all 8 secrets are present

2. **Check workflow logs**:
   - Go to: https://github.com/PriyaKPatel/Text-to-Code-Generation/actions
   - Click on the failed workflow
   - Read the error messages

3. **Common issues**:
   - Wrong AWS credentials → Update AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
   - Wrong SSH key → Update EC2_SSH_KEY with correct .pem file content
   - EC2 host changed → Update EC2_HOST with new IP

---

## Quick Reference Commands

```bash
# Get AWS Account ID
aws sts get-caller-identity --query Account --output text

# View AWS credentials
cat ~/.aws/credentials

# View SSH key
cat ~/Downloads/text-to-code-key.pem

# Check EC2 is accessible
ssh -i ~/Downloads/text-to-code-key.pem ubuntu@3.85.224.148 "echo 'Connection successful'"
```

---

## 🎉 Benefits of CI/CD

Once set up, every push to `main` will:
- ✅ Run tests automatically
- ✅ Build and deploy without manual steps
- ✅ Ensure code quality with linting
- ✅ Deploy to production in ~5 minutes
- ✅ Rollback easily if needed

---

**Ready to go live? Add the secrets and push a change!** 🚀

