import { useState } from 'react'
import {Spinner} from "./component/Spinner"
import './App.css'
import axios from "axios"

function App() {
  const [files, setFiles] = useState(null)
  const [response,setResponse] =useState(null)
  const[loading,setLoading] =useState(false)

  async function handleUpload(){
    const formData = new FormData()
    formData.append("file",files)
    setLoading(true)
    try{
      const res = await axios.post(`http://localhost:8000/upload-resume`,formData)
    setLoading(false)
    setResponse(res.data)
   }catch(err){
    setResponse(err)
   }
    
  }

  return (
    <>
      <div className='App'>
      <h1>Automated Resume Grader</h1>
      </div>
      <div>
        <input type="file" accept='.pdf' onChange={(e)=>{setFiles(e.target.files[0])}}  placeholder='choose your Resume'/>
      </div>
      <div>
        <button onClick={handleUpload} >Upload</button>
      </div>

      {loading && <Spinner/>}
      <div>
             {response && (
        <div>
          {/*<h2>Score: {response.score}/100</h2>*/}
          <ul>
            {response.parsed_data.personal_info.name}
          </ul>
        </div>
      )}
      </div>
     
        
    </>
  )
}

export default App
