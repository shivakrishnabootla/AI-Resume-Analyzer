<!-- Features -->
## Features 🤦‍♂️
### Client: -
- **AI-Powered Resume Analysis** — Extracts and analyzes key resume data using advanced parsing techniques
- **Location & Miscellaneous Data Fetching** — Uses geolocation services to fetch city, state, and country information
- **Skill Extraction & Analysis** — Parses skills, keywords, and professional experience from resumes
- **Intelligent Recommendations** — Suggests:
  - Missing skills to add
  - Predicted job roles and career paths
  - Relevant courses and certifications
  - Actionable resume improvement tips
  - Recommended interview preparation videos
- **Resume Scoring** — Calculates an overall resume quality score based on multiple criteria
- **Modern Dark Theme UI** — Professional black and gold interface with smooth animations
- **Real-time Processing** — Instant feedback and recommendations upon resume upload

### Admin: -
- **Comprehensive User Data Dashboard** — View all applicant data in organized, filterable tabular format
- **CSV Export** — Download user data and analytics in CSV format for further analysis
- **Resume File Management** — Access all uploaded resumes stored in the Uploaded_Resumes folder
- **Feedback Analytics** — Track user feedback and satisfaction ratings
- **Advanced Visualizations** — Pie charts and analytics for:
  - User ratings distribution
  - Predicted fields/roles analysis
  - Experience level distribution
  - Resume score distribution
  - Active user count tracking
  - Geographic data (City, State, Country)
- **Admin Credentials** — Secure login with admin verification

### Feedback: -
- **User Feedback Form** — Intuitive form for users to submit ratings and comments
- **1-5 Star Rating System** — Collect quantified user satisfaction metrics
- **Analytics Dashboard** — Visualize overall ratings with pie charts and distribution analysis
- **Comment History** — Track and display all past user feedback and comments
- **Real-time Analytics** — Immediate feedback aggregation and trend analysis 

## Requirements 😅
### Prerequisites — Install these to get started:

1. **Python 3.9.12+** — [Download](https://www.python.org/downloads/release/python-3912/)
2. **MySQL Server 8.0+** — [Download](https://www.mysql.com/downloads/)
3. **Visual Studio Code** (Recommended) — [Download](https://code.visualstudio.com/Download)
4. **Visual Studio Build Tools for C++** — [Download](https://aka.ms/vs/17/release/vs_BuildTools.exe) (required for some Python packages)
5. **Git** (Optional, for cloning) — [Download](https://git-scm.com/downloads)

### System Requirements:
- **OS**: Windows 10+ / macOS / Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: 2GB for virtual environment and dependencies

## Setup & Installation 👀

### Quick Start (Windows PowerShell)

**1. Clone or Download the Repository**
```powershell
git clone https://github.com/shivakrishnabootla/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

**2. Create and Activate Virtual Environment**
```powershell
# Create virtual environment
py -m venv .venv

# Activate virtual environment (PowerShell)
.\.venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Alternative (Command Prompt):
# .\.venv\Scripts\activate.bat
```

**3. Install Dependencies**
```powershell
cd App
pip install -r requirements.txt
py -m spacy download en_core_web_sm
```

**4. Configure Database**
- Open MySQL Workbench or MySQL Command Line
- Create a new database named `cv`:
  ```sql
  CREATE DATABASE cv;
  ```
- Update credentials in `App/App.py` (around line 95-106):
  ```python
  mydb = mysql.connector.connect(
      host="localhost",        # Change if needed
      user="root",             # Change to your MySQL username
      password="123456",       # Change to your MySQL password
      database="cv"            # Database name
  )
  ```

**5. Update pyresparser Module**
- Navigate to `venvapp\Lib\site-packages\pyresparser\` (or your venv equivalent)
- Replace `resume_parser.py` with the updated version from `pyresparser\resume_parser.py` in the project root

**6. Run the Application**
```powershell
py -m streamlit run App.py --server.port 8503
```

The app will open in your default browser at `http://localhost:8503`

**Troubleshooting Port Issues:**
If port 8503 is in use, change it:
```powershell
py -m streamlit run App.py --server.port 8504
```

### Installation Video Guide
For a visual walkthrough, check out this [setup video](https://youtu.be/WFruijLC1Nc)

## Known Issues & Solutions 🤪

### GeocoderUnavailable Error
**Issue**: `GeocoderUnavailable` error during resume parsing
**Solution**: Check your internet connection and network speed. Ensure Nominatim/geolocation services are accessible.

### spaCy Model Not Found
**Issue**: `ModuleNotFoundError: No module named 'en_core_web_sm'`
**Solution**: 
```powershell
py -m spacy download en_core_web_sm
```

### MySQL Connection Failed
**Issue**: Cannot connect to MySQL database
**Solutions**:
1. Verify MySQL Server is running
2. Check username and password in `App/App.py` (lines 95-106)
3. Ensure database `cv` exists:
   ```sql
   CREATE DATABASE cv;
   ```
4. Verify port 3306 is accessible

### Virtual Environment Issues
**Issue**: Python not found or venv broken
**Solution**: Recreate the virtual environment:
```powershell
Remove-Item -Recurse -Force .venv
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r App\requirements.txt
```

## Common Installation & Setup Issues 🤧

For detailed troubleshooting steps and visual walkthroughs, check out this [installation guide video](https://youtu.be/WFruijLC1Nc)

Having issues? Feel free to <a href="mailto:dnoobnerd@gmail.com?subject=AI%20Resume%20Analyzer%20-%20Installation%20Issue&body=Name:%20-%0D%0A%0D%0ADesignation:%20-%0D%0A%0D%0AProblem Description:%20-%0D%0A%0D%0APlease include error messages and screenshots">contact support</a>

## Usage 📖

1. **Start the Application**
   ```powershell
   py -m streamlit run App.py --server.port 8503
   ```

2. **User Portal (Client)**
   - Upload a PDF resume
   - The app automatically analyzes and extracts key information
   - View personalized recommendations for skills, courses, and roles
   - Check your resume score and improvement tips
   - Watch recommended interview preparation videos
   - Example: Try the sample resume in the `Uploaded_Resumes` folder

3. **Feedback Section**
   - Rate your experience (1-5 stars)
   - Submit detailed feedback and comments
   - View historical ratings and community feedback

4. **Admin Dashboard**
   - **Login**: Username: `admin` | Password: `admin@resume-analyzer`
   - View all applicant data in table format
   - Export user data to CSV
   - Analyze trends with pie charts (ratings, roles, experience levels, locations)
   - Monitor upload statistics

## UI & Theme 🎨

The application features a professional dark theme with:
- **Color Scheme**: Black background, white text, gold (#ffd700) accents, and blue (#0969da) highlights
- **Responsive Design**: Mobile-friendly interface with smooth animations
- **Interactive Charts**: Plotly-powered analytics and visualizations
- **Cloud Animation**: Decorative animated cloud elements
- **GitHub-style Cards**: Modern card-based layout for data presentation

To customize the theme, edit the CSS variables in `App/App.py` (lines ~195-210):
```python
--primary-gold: #ffd700
--primary-blue: #0969da
--text-light: #ffffff
```

<!-- Roadmap -->
## Roadmap 🛵

### ✅ Completed Features
- [x] Predict user experience level from resume
- [x] Advanced resume scoring based on multiple criteria
- [x] Role-specific recommendations (Web, Android, iOS, Data Science)
- [x] Comprehensive skill and project extraction
- [x] Location-based analytics and tracking
- [x] Interactive admin dashboard with charts
- [x] CSV export functionality
- [x] Professional dark theme UI

### 🚀 Planned Features
- [ ] Multi-language resume support
- [ ] Extended role recommendations (DevOps, Cloud, ML Engineering, etc.)
- [ ] Resume template suggestions
- [ ] Automated email notifications
- [ ] API endpoint for external integrations
- [ ] User profile persistence and history tracking
- [ ] Advanced NLP-based skill gap analysis
- [ ] Resume plagiarism detection

## Contributing 🤘

We welcome contributions from the community! Here's how to contribute:

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/YourFeature`
3. Make your changes and test thoroughly
4. Commit with clear messages: `git commit -m "Add YourFeature"`
5. Push to your branch: `git push origin feature/YourFeature`
6. Open a Pull Request with a detailed description

### For Major Changes
Please open an issue first to discuss what you would like to change.

### Guidelines
- Follow PEP 8 style guidelines for Python code
- Add comments to explain complex logic
- Test your changes before submitting
- Update documentation as needed

### Resources
- [Project Synopsis](https://github.com/shivakrishnabootla/AI-Resume-Analyzer/blob/main/RESUME%20ANALYSER%20SYNOPSIS.pdf)
- Questions or suggestions? Open an issue on the repository or contact the maintainers

## Acknowledgements 🤗

We thank the following resources and contributors for making this project possible:

- [Dr. Bright](https://www.linkedin.com/in/mrbriit/) - [The Full Stack Data Scientist BootCamp](https://www.udemy.com/course/the-full-stack-data-scientist-bootcamp/)
- [Resume Parser with Natural Language Processing](https://www.academia.edu/32543544/Resume_Parser_with_Natural_Language_Processing)
- [pyresparser Library](https://github.com/OmkarPathak/pyresparser)
- spaCy and NLTK teams for NLP libraries
- Streamlit team for the amazing framework
- MySQL for reliable database management

## License 📜

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact & Support 💬

Have questions or need help?
- **GitHub Issues**: Open an issue on the repository
- **Email**: Contact the project maintainers through GitHub

## Latest Updates 🔄

### Version 2.0 (Current)
- ✨ Professional dark theme with gold and blue accents
- 🎨 Enhanced UI with cloud animations
- 🎯 Improved resume parsing accuracy
- 📊 Advanced analytics dashboard
- 🚀 Better performance and error handling

---

### Built with ❤️ by Shiva Krishna & Team
