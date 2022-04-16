import './style.css'
import React, { useState } from 'react';
import axios from 'axios';

export default function MainContainer() {

    const [selectedFile, setSelectedFile] = useState();
    //const [isFilePicked, setIsFilePicked] = useState(false);
    const [rezultat, setRezultat] = useState();

    const fileSelectedHandler = (event) => {
       setSelectedFile(event.target.files[0]);
       //setIsFilePicked(true);
    }

    const fileUplaodHandler = () => {
        const fd = new FormData();
        fd.append('img', selectedFile);
        axios.post('http://127.0.0.1:5000/upload', fd).then(res => {    
            console.log(res.data.result)
            setRezultat(res.data.result);
        }).catch(err => {
            console.log(err)
        })
        
    }

    return (
        <main>
      <div class="container-principal">
        <div class="content-container">
          <h1>Upload a photo ⤵</h1>
          <input
            type="file"
            id="upload-button"
            class="input-upload"
            accept="image/png, image/jpeg"
            onChange={fileSelectedHandler}
          />
          <p class="p-scanner">
            Press the 'browse' button to upload the image you want to convert
            into a text file.
          </p>
          <button onClick={fileUplaodHandler}>
            Convert to text
          </button>
          <hr></hr>
          <textarea value={rezultat} rows="5" cols="50"/>


        </div>
      </div>
    </main>
    )
}