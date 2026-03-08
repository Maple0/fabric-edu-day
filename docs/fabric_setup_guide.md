# Fabric Environment Setup Guide

Pre-demo environment setup instructions for the Fabric IQ Education Demo.

---

## Requirements

| Requirement | Details |
|------------|---------|
| Microsoft Fabric capacity | F64 or higher (required for Copilot) |
| Azure AD tenant | With Fabric enabled |
| User permissions | Workspace Admin or Contributor |
| Copilot | Enabled in Fabric tenant admin settings |
| Data Agents | Enabled in Fabric tenant admin settings |
| Browser | Microsoft Edge or Chrome (latest) |

---

## Step 1: Create Fabric Workspace

1. Navigate to [app.fabric.microsoft.com](https://app.fabric.microsoft.com)
2. Click **Workspaces** → **New workspace**
3. Name: `Fabric IQ Education Demo` (or your preferred name)
4. Under **Advanced**, select your F64+ capacity
5. Click **Apply**

---

## Step 2: Create Lakehouse

1. In your workspace, click **New** → **Lakehouse**
2. Name: `university_lakehouse`
3. Click **Create**

---

## Step 3: Upload Notebooks

Upload all 6 notebooks from the `notebooks/` directory:

1. In the workspace, click **Import** → **Notebook** → **From this computer**
2. Upload each file:
   - `01_data_generation_and_ingestion.ipynb`
   - `02_star_schema_delta_tables.ipynb`
   - `03_semantic_model_configuration.ipynb`
   - `04_fabric_iq_copilot_demo.ipynb`
   - `05_data_agent_staff_persona.ipynb`
   - `06_data_agent_student_persona.ipynb`

**Alternatively:** Upload Parquet files directly if you want to skip Notebook 01.

---

## Step 4: Attach Lakehouse to Notebooks

For each notebook:

1. Open the notebook
2. Click **Add Lakehouse** (left panel)
3. Select **Existing lakehouse** → choose `university_lakehouse`
4. Click **Add**

The Lakehouse path `/lakehouse/default/` will now resolve correctly in all code cells.

---

## Step 5: Run Notebooks 01 and 02

### Notebook 01: Data Generation & Ingestion

1. Open `01_data_generation_and_ingestion`
2. Click **Run all**
3. Wait for completion (~2-3 minutes)
4. Verify: Navigate to Lakehouse → **Files** → confirm `raw/` and `parquet/` folders contain 13 tables each

### Notebook 02: Star Schema Delta Tables

1. Open `02_star_schema_delta_tables`
2. Click **Run all**
3. Wait for completion (~3-5 minutes)
4. Verify: Navigate to Lakehouse → **Tables** → confirm 13 Delta tables listed
5. Check row counts match expected volumes

---

## Step 6: Create Semantic Model

Follow the detailed instructions in `docs/semantic_model_setup.md`:


---

## Step 7: Enable Copilot

1. Go to **Fabric Admin Portal** → **Tenant settings**
2. Under **Copilot and Azure OpenAI Service**:
   - Enable **Users can use Copilot and other features powered by Azure OpenAI**
   - Set to your security group or **Entire organization**
3. Click **Apply**
4. Wait up to 15 minutes for settings to propagate

---

## Step 8: Create Data Agents

### Staff Agent

1. In the workspace, click **New** → **Data Agent**
2. Name: `University Staff Analytics Assistant`
3. Connect to the `university-analytics-model` semantic model
4. Add system prompt (from Notebook 05)
5. Test with sample questions

### Student Agent

1. Create another Data Agent
2. Name: `Student Self-Service Assistant`
3. Connect to the `university-analytics-model` semantic model
4. Ensure the Student RLS role is active for the connected user
5. Add system prompt (from Notebook 06)
6. Test with sample questions using a test student account

---

## Step 9: Pre-Demo Verification

Run through this checklist before presenting:

### Data Layer
- [ ] Lakehouse `university_lakehouse` exists
- [ ] 13 Parquet files under `Files/parquet/`
- [ ] 13 Delta tables under `Tables/`
- [ ] Row counts match expected values

### Semantic Model
- [ ] `university-analytics-model` model exists
- [ ] 13 relationships defined (no warnings)
- [ ] All DAX measures calculate correctly
- [ ] 4 hierarchies created
- [ ] RLS roles configured and tested

### AI Features
- [ ] Copilot enabled and responding
- [ ] Staff Data Agent answers questions correctly
- [ ] Student Data Agent scoped to single student
- [ ] All demo prompts tested at least once

### Browser Tabs
Pre-load these tabs for smooth demo transitions:
1. Lakehouse → Tables view
2. Notebook 01 (completed run)
3. Notebook 02 (completed run)
4. Power BI report (with Copilot panel)
5. Staff Data Agent
6. Student Data Agent

---

## Alternative: Upload Pre-Generated Data

If you prefer not to run Notebook 01 in Fabric:

1. Run locally: `python scripts/generate_data.py --format parquet --output-dir data`
2. In the Lakehouse, click **Upload** → **Upload files**
3. Upload all 13 Parquet files from `data/parquet/` to `Files/parquet/`
4. Then run Notebook 02 to create Delta tables from the uploaded Parquet files

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| `pip install faker` fails | Check network access from Fabric Runtime; try `%pip install faker --quiet` |
| Lakehouse path not found | Ensure Lakehouse is attached to the notebook (left panel) |
| Delta table write fails | Check workspace capacity is not paused; verify Lakehouse permissions |
| Semantic model refresh error | Verify Delta tables exist; try manual refresh |
| Copilot not available | Confirm F64+ capacity; check tenant admin settings; wait 15 min after enabling |
| Data Agent not connecting | Verify semantic model is published; check model permissions |
| RLS not applying | Ensure user is added to the correct role; test with "View as role" |
