# Pronunciation Practice Portal - Frontend

React frontend for the English Pronunciation Practice Portal with AI-powered feedback.

## Features

### For Students
- 🎤 **Record Pronunciation** - Browser-based audio recording
- ⚡ **Instant AI Feedback** - Immediate scores and personalized feedback
- 📊 **Detailed Scores** - Pronunciation, accuracy, fluency, completeness
- 🎯 **Phoneme Analysis** - Know exactly which sounds need work
- 📈 **Progress Tracking** - Daily stats, streaks, and improvement trends
- 🏆 **Grading System** - Letter grades (A+ to F)

### For Teachers
- 📝 **Review Submissions** - See all student recordings and AI feedback
- ✏️ **Modify Feedback** - Override or enhance AI-generated feedback
- 📊 **Analytics** - Class performance, challenging words, student progress
- 👥 **Student Management** - View all students and their performance
- 🎯 **Flag for Practice** - Mark recordings that need additional work

## Tech Stack

- **React 18** - UI framework
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Vite** - Build tool and dev server

## Prerequisites

- Node.js 16+
- npm or yarn
- Backend API running on http://localhost:8000

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will open at http://localhost:3000

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Auth/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── Student/
│   │   │   ├── StudentDashboard.jsx
│   │   │   └── RecordingInterface.jsx
│   │   ├── Teacher/
│   │   │   ├── TeacherDashboard.jsx
│   │   │   └── ReviewSubmission.jsx
│   │   └── Common/
│   │       └── Navbar.jsx
│   ├── services/
│   │   ├── api.js
│   │   ├── authService.js
│   │   ├── wordService.js
│   │   ├── studentService.js
│   │   └── teacherService.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## Available Scripts

### Development
```bash
npm run dev
```
Starts the development server with hot reload at http://localhost:3000

### Build
```bash
npm run build
```
Creates an optimized production build in the `dist/` directory

### Preview
```bash
npm run preview
```
Preview the production build locally

## Configuration

### API Base URL

The frontend is configured to proxy API requests to http://localhost:8000 during development.

This is configured in `vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

For production, update the `API_BASE_URL` in `src/services/api.js`.

## Features Walkthrough

### Student Flow

1. **Login/Register**
   - Students register with username, email, and password
   - Choose "Student" role during registration

2. **Practice Dashboard**
   - Daily word challenge automatically loaded
   - Search for any word to practice
   - View word definition, phonetic, and example

3. **Recording**
   - Click microphone button to start recording
   - Speak the word clearly
   - Click stop button when done
   - Preview your recording
   - Submit for assessment

4. **Instant Feedback**
   - See pronunciation score immediately
   - Get detailed breakdown (accuracy, fluency, completeness)
   - Read personalized AI feedback
   - View letter grade
   - See phoneme-level analysis

5. **Progress Tracking**
   - View weekly statistics
   - Track practice streak
   - See average scores
   - Review past recordings and feedback

### Teacher Flow

1. **Login**
   - Login with teacher credentials

2. **Submissions Tab**
   - View all student submissions
   - See which have AI feedback vs manual review
   - Click on submission to review in detail

3. **Review Submission**
   - Listen to student recording
   - See automated scores and phoneme analysis
   - Read current AI-generated feedback
   - Modify or replace feedback
   - Assign custom grade
   - Flag for additional practice
   - Save changes

4. **Students Tab**
   - View all registered students
   - See total recordings and average scores per student

5. **Analytics Tab**
   - View overall statistics
   - See most practiced words
   - Identify challenging words
   - Track pending reviews

## Browser Compatibility

### Audio Recording Requirements

The recording feature requires:
- Modern browser with MediaRecorder API support
- Microphone access permission
- HTTPS in production (or localhost for development)

**Supported Browsers:**
- Chrome/Edge 49+
- Firefox 25+
- Safari 14+
- Opera 36+

**Not Supported:**
- Internet Explorer
- Older mobile browsers

## Styling

The app uses Tailwind CSS for styling with a custom color scheme:

**Primary Colors:**
- Primary: Blue (#3b82f6)
- Success: Green
- Warning: Yellow
- Error: Red

**Components:**
Custom Tailwind components are defined in `src/index.css`:
- `.btn-primary` - Primary action buttons
- `.btn-secondary` - Secondary buttons
- `.input-field` - Form inputs
- `.card` - Container cards

## Development Tips

### Enable Microphone Access

When testing locally, make sure to:
1. Allow microphone access when prompted
2. Use HTTPS or localhost (HTTP won't work for microphone in modern browsers)

### API Connection Issues

If you see connection errors:
1. Ensure backend is running on http://localhost:8000
2. Check CORS settings in backend
3. Verify proxy configuration in vite.config.js

### Hot Reload

Vite provides instant hot module replacement (HMR). Changes to components will reflect immediately without full page reload.

## Building for Production

### 1. Build the App

```bash
npm run build
```

This creates a `dist/` folder with optimized static files.

### 2. Update API URL

Before building for production, update the API base URL in `src/services/api.js`:

```javascript
const API_BASE_URL = 'https://your-api-domain.com';
```

### 3. Deploy

The `dist/` folder can be deployed to:
- **Netlify** - Drag and drop
- **Vercel** - Connect GitHub repo
- **AWS S3 + CloudFront**
- **Azure Static Web Apps**
- **Any static hosting service**

### Example: Deploy to Netlify

```bash
npm run build
npx netlify-cli deploy --prod --dir=dist
```

## Environment Variables

Create a `.env` file for environment-specific configuration:

```env
VITE_API_URL=http://localhost:8000
```

Access in code:
```javascript
const apiUrl = import.meta.env.VITE_API_URL;
```

## Troubleshooting

### Microphone Not Working

**Problem:** Recording button doesn't work

**Solutions:**
- Check browser console for errors
- Ensure you're on localhost or HTTPS
- Grant microphone permission
- Try a different browser

### API Errors

**Problem:** "Network Error" or "Failed to fetch"

**Solutions:**
- Verify backend is running on port 8000
- Check CORS configuration in backend
- Ensure no firewall blocking requests
- Check browser console for details

### Styling Issues

**Problem:** Tailwind classes not applying

**Solutions:**
- Run `npm install` to ensure all dependencies installed
- Restart dev server after tailwind.config.js changes
- Check for typos in class names
- Verify `index.css` imports Tailwind directives

## Testing

### Manual Testing Checklist

**Student Features:**
- [ ] Register new student account
- [ ] Login with student credentials
- [ ] Search for a word
- [ ] Record pronunciation
- [ ] View instant feedback
- [ ] Check progress stats
- [ ] View past recordings

**Teacher Features:**
- [ ] Login with teacher credentials
- [ ] View student submissions
- [ ] Listen to recordings
- [ ] Modify AI feedback
- [ ] Assign custom grades
- [ ] View analytics
- [ ] Check student list

## Performance

### Optimization Tips

1. **Code Splitting** - Vite automatically code-splits routes
2. **Lazy Loading** - Large components can be lazy-loaded
3. **Image Optimization** - Use optimized image formats
4. **Caching** - Service worker for offline support (optional)

### Bundle Size

Current production build size (approximate):
- Vendor chunks: ~150KB (React, Router, etc.)
- App code: ~50KB
- Total (gzipped): ~200KB

## Security

### Authentication

- JWT tokens stored in localStorage
- Tokens automatically attached to API requests
- Auto-redirect on 401 Unauthorized
- Tokens cleared on logout

### Best Practices

- Never commit `.env` files
- Validate all user inputs
- Sanitize displayed content
- Use HTTPS in production
- Implement CSP headers

## Contributing

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## License

Educational project for ILP CW3

## Support

For issues or questions:
- Check browser console for errors
- Review backend logs
- Ensure backend is running
- Verify API endpoints are accessible

---

Built with ❤️ using React + Vite
