const express = require('express');
const multer = require('multer');
const app = express();
const { exec } = require('child_process');
const fs = require('fs')

app.listen(3000);
app.set('view engine', 'ejs');
app.use(express.static('public'));
app.use(express.urlencoded({ extended: true }))

var jdata = ""

// Function to execute Python code
function runPythonScript(scriptPath, args, callback) {
    // Build the command to execute the Python script
    const command = `python ${scriptPath} ${args.join(' ')}`;
    // Execute the command
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing Python script: ${error}`);
        return;
      }
      // Invoke the callback with the script output
      callback(stdout);
    });
  }

// Set up Multer storage
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
      cb(null, 'uploads/'); // Destination folder for uploaded files
    },
    filename: (req, file, cb) => {
      cb(null, Date.now() + '-' + file.originalname); // File name with a timestamp prefix
    }
  });
// Create a Multer instance with the storage configuration
const upload = multer({ storage: storage });

// Define a landing route 
app.get('/', (req, res) => {
    res.render('index', { title: 'home' });
})
// Define a route for json download
app.get('/download', (req, res) => {
  // Set response headers to specify file name and content type
  res.setHeader('Content-Disposition', 'attachment; filename="data.json"');
  res.setHeader('Content-Type', 'application/json');
  // Send the JSON data as a downloadable file
  res.send(jdata, null, 2);
});

// Define a route for file uploads
app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded.');
  }
  //res.send('File uploaded successfully.');
  ifcpath = req.file.path
  runPythonScript('getRamps.py', ["--input "+ ifcpath], (output) => {
    console.log(output);
  });
  const filePath = './views/json/dump';
  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      console.error(err);
      return res.status(500).send('Error reading JSON file');
    }
    console.log(data)
    jdata = data
    
    res.render('result', {
      title: 'results',
      data: data
  })
  });  
});
