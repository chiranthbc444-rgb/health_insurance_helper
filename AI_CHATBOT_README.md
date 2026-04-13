# AI Chatbot Integration Setup

## Overview
This Django application now includes an AI-powered chatbot for insurance assistance with document upload and analysis capabilities.

## Features
- **AI Chatbot**: Interactive chat widget for insurance queries
- **Document Upload**: Secure file upload with validation
- **OCR & AI Analysis**: Automatic document text extraction and AI-powered analysis
- **Claim Eligibility Check**: Intelligent assessment of claim readiness
- **Chat History**: Persistent conversation storage
- **Document Management**: Organized document storage and retrieval

## Setup Instructions

### 1. Install Required Packages
```bash
pip install openai pytesseract Pillow PyMuPDF requests
```

### 2. Configure API Keys
Add your OpenAI API key to `settings.py`:
```python
OPENAI_API_KEY = 'your-openai-api-key-here'
```

### 3. Install Tesseract OCR (for Windows)
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and note the installation path
3. Update the path in `ai_service.py` if needed

### 4. Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Media Files Setup
The app automatically creates a `media/` directory for uploaded files.

## API Endpoints

### Chatbot API
- **URL**: `/api/chatbot/`
- **Method**: POST
- **Data**: `{"message": "user query", "session_id": "optional"}`
- **Response**: `{"success": true, "response": "AI response"}`

### Document Upload
- **URL**: `/upload-document/`
- **Method**: POST
- **Data**: `document` (file), `document_type` (string)

## Document Types Supported
- Insurance Policy
- Claim Form
- Medical Bill
- Prescription
- ID Proof
- Other

## File Restrictions
- **Allowed Types**: PDF, JPG, JPEG, PNG
- **Maximum Size**: 10MB
- **Storage**: User-specific directories in `media/documents/`

## AI Analysis Features
- **Text Extraction**: OCR for images, direct parsing for PDFs
- **Policy Information**: Extracts policy number, type, coverage, validity
- **Claim Assessment**: Determines document completeness and eligibility
- **Recommendations**: Provides next steps for users

## Security Features
- User authentication required for uploads
- File type and size validation
- Private document storage
- CSRF protection on all forms

## Usage Examples

### Basic Chat
```javascript
fetch('/api/chatbot/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token
    },
    body: JSON.stringify({
        message: "What is covered under my health insurance?",
        session_id: "user_session_123"
    })
});
```

### Document Upload
```html
<form method="post" enctype="multipart/form-data" action="/upload-document/">
    {% csrf_token %}
    <select name="document_type">
        <option value="policy">Insurance Policy</option>
    </select>
    <input type="file" name="document" accept=".pdf,.jpg,.png">
    <button type="submit">Upload</button>
</form>
```

## Customization

### AI Prompts
Modify prompts in `ai_service.py` to customize AI behavior.

### UI Styling
Update CSS in `chatbot.html` and `base_modern.html` for custom styling.

### Document Types
Add new document types in the `DOCUMENT_TYPES` tuple in `models.py`.

## Troubleshooting

### Common Issues
1. **Tesseract not found**: Install Tesseract and update path
2. **OpenAI API errors**: Check API key and quota
3. **File upload fails**: Check file permissions and media directory
4. **OCR fails**: Ensure image quality and supported formats

### Logs
Check Django logs for detailed error information.

## Future Enhancements
- Multiple AI provider support (Google Gemini, Claude)
- Batch document processing
- Advanced claim workflow automation
- Integration with external insurance systems