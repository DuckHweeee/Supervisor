# Smart Building AI - Auto-Training System Guide

## 🎯 Overview
Your Smart Building AI Assistant now has a comprehensive auto-training system that automatically trains the AI whenever you add new content like the IIC_EIU_Overview.docx file.

## 📁 Current Setup
- ✅ **IIC Document**: `smart_building_data/IIC_EIU_Overview.docx` (38KB)
- ✅ **Training Scripts**: 4 different training scripts available
- ✅ **Knowledge Base**: 160 document chunks currently loaded
- ✅ **Auto-Training**: File watcher system ready

## 🚀 Quick Start

### Option 1: Use the Menu System (Easiest)
```bash
# Double-click this file or run in Command Prompt:
auto_training_menu.bat
```

### Option 2: Use Individual Scripts

#### Train on IIC Document Only
```bash
python enhanced_training.py --iic
```

#### Train on All Documents
```bash
python enhanced_training.py --batch
```

#### Start Auto-Training Watcher
```bash
python simple_auto_trainer.py
```

#### Show Training Status
```bash
python training_summary.py
```

## 🔄 Auto-Training Process

### What Gets Trained Automatically:
- **Document Types**: PDF, DOCX, DOC, TXT, JSON, MD, CSV, XLSX
- **Location**: Files in `smart_building_data/` folder
- **Trigger**: When files are added, modified, or updated

### What Gets Ignored:
- System files (training logs, temporary files)
- Hidden files (starting with . or ~)
- Backup files (.bak, .tmp)

### Document Type Detection:
- **IIC/EIU files** → `university_overview` (High Priority)
- **HVAC files** → `hvac_manual` (Medium Priority)
- **Lighting files** → `lighting_specifications` (Medium Priority)
- **Security files** → `security_manual` (Medium Priority)
- **Energy files** → `energy_management` (Medium Priority)
- **Other files** → `general_documentation` (Low Priority)

## 📊 Training Status and Logs

### Training Logs Available:
- `training_log.json` - General training sessions
- `iic_training_log.json` - IIC-specific training sessions
- `auto_training_log.json` - Auto-watcher training sessions

### Current Knowledge Base Stats:
- **Total Chunks**: 160 documents
- **Document Types**: 7 different types
- **Auto-Trained**: 2 documents
- **Training Methods**: Auto, Manual, Batch

## 🌐 Using the Streamlit App

### Start the App:
```bash
streamlit run streamlit_app.py
```

### Available Training Controls:
- **🎯 Train on IIC_EIU_Overview** - One-click IIC training
- **📚 Train on All Documents** - Batch training with progress bar
- **📊 Training Status** - View recent training sessions
- **🔍 Auto-Training Setup** - Instructions for file watcher

### Test Your Training:
Ask questions like:
- "What is IIC?"
- "Tell me about Eastern International University"
- "Information about EIU Innovation Center"
- "What programs does EIU offer?"

## 💡 Adding New Content

### Method 1: Add and Auto-Train
1. **Add documents** to `smart_building_data/` folder
2. **Start auto-watcher**: `python simple_auto_trainer.py`
3. **Files are automatically trained** when detected

### Method 2: Manual Training
1. **Add documents** to `smart_building_data/` folder
2. **Run batch training**: `python enhanced_training.py --batch`
3. **Check results**: `python training_summary.py`

## 🔧 Troubleshooting

### If Training Fails:
1. Check if document is in `smart_building_data/` folder
2. Verify file format is supported
3. Check training logs for error messages
4. Run `python training_summary.py` to see current state

### If Auto-Training Doesn't Work:
1. Ensure file watcher is running: `python simple_auto_trainer.py`
2. Check if file is being ignored (system files, hidden files)
3. Verify file has supported extension
4. Check auto-training log for activities

### If Streamlit App Has Issues:
1. Restart the app: `Ctrl+C` then `streamlit run streamlit_app.py`
2. Check browser console for errors
3. Try training manually using command line scripts

## 📈 Performance Tips

### For Large Documents:
- Documents are automatically chunked for optimal performance
- Vietnamese content is extracted and English summaries are added
- Metadata is enhanced for better search relevance

### For Better Results:
- Use descriptive file names (e.g., "IIC_EIU_Overview.docx")
- Organize documents by type in subfolders if needed
- Train on related documents together for better context

## 🎯 Next Steps

1. **Test the current setup**:
   ```bash
   python training_summary.py
   ```

2. **Start auto-training**:
   ```bash
   python simple_auto_trainer.py
   ```

3. **Use the Streamlit app**:
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Add more content** to `smart_building_data/` folder

5. **Monitor training logs** to ensure everything works correctly

## 🆘 Support

If you encounter any issues:
1. Check the training logs for error messages
2. Run `python training_summary.py` to see current state
3. Try manual training first: `python enhanced_training.py --iic`
4. Restart the auto-training watcher if needed

---

## 🎉 You're All Set!

Your Smart Building AI Assistant is now equipped with:
- ✅ **IIC_EIU_Overview.docx** trained and ready
- ✅ **Auto-training system** monitoring for new content
- ✅ **Multiple training methods** (manual, batch, auto)
- ✅ **Comprehensive logging** and status tracking
- ✅ **Easy-to-use interfaces** (Streamlit app + command line)

**Every time you add new content, the AI will automatically learn from it!** 🚀
