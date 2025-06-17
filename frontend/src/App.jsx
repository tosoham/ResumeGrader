import { useState } from 'react'
import {Spinner} from "./component/Spinner"
import './App.css'
import axios from "axios"

url = `${import.meta.env.VITE_API_URL}` || `http://localhost:8000`;

function App() {
  const [files, setFiles] = useState(null)
  const [response,setResponse] = useState(null)
  const [loading,setLoading] = useState(false)

  async function handleUpload(){
    const formData = new FormData()
    formData.append("file",files)
    setLoading(true)
    try{
      const res = await axios.post(`${url}/grade-resume`,formData)
      setLoading(false)
      setResponse(res.data)
    }catch(err){
      setLoading(false)
      setResponse(null)
      console.error("Upload failed:", err)
    }
  }

  return (
    <>
      <div className='App'>
        <h1>Automated Resume Grader</h1>
      </div>
      <div>
        <input 
          type="file" 
          accept='.pdf' 
          onChange={(e)=>{setFiles(e.target.files[0])}}  
          placeholder='choose your Resume'
        />
      </div>
      <div>
        <button onClick={handleUpload} disabled={!files || loading}>
          Upload
        </button>
      </div>

      {loading && <Spinner/>}
      
      <div>
        {response && response.grading_result && (
          <div>
            <h2>
              Your Overall Score is{" "}
              {response.grading_result.overall_score} out of 100 and
              your section scores are: personal info{" "}
              {response.grading_result.section_scores?.personal_info || 'N/A'}{" "}
              , experience{" "}
              {response.grading_result.section_scores?.experience || 'N/A'}{" "}
              , education{" "}
              {response.grading_result.section_scores?.education || 'N/A'}{" "}
              , skills{" "}
              {response.grading_result.section_scores?.skills || 'N/A'}
              , projects{" "}
              {response.grading_result.section_scores?.projects || 'N/A'}
            </h2>
            <br />
            
            {/* Personal Information */}
            {response.parsed_data?.personal_info && (
              <div>
                <h3>Personal Information</h3>
                <p>Name: {response.parsed_data.personal_info.name}</p>
                <p>Email: {response.parsed_data.personal_info.email}</p>
                <p>Phone: {response.parsed_data.personal_info.phone}</p>
                {response.parsed_data.personal_info.address && (
                  <p>Address: {response.parsed_data.personal_info.address}</p>
                )}
                {response.parsed_data.personal_info.linkedin && (
                  <p>LinkedIn: {response.parsed_data.personal_info.linkedin}</p>
                )}
                {response.parsed_data.personal_info.github && (
                  <p>GitHub: {response.parsed_data.personal_info.github}</p>
                )}
              </div>
            )}

            {/* Education */}
            {response.parsed_data?.education && response.parsed_data.education.length > 0 && (
              <div>
                <h3>Education</h3>
                {response.parsed_data.education.map((edu, index) => (
                  <div key={index}>
                    <h4>{edu.institution}</h4>
                    <p>{edu.degree} in {edu.field_of_study}</p>
                    <p>{edu.year}</p>
                    {edu.gpa && <p>GPA: {edu.gpa}</p>}
                  </div>
                ))}
              </div>
            )}

            {/* Experience */}
            {response.parsed_data?.experience && response.parsed_data.experience.length > 0 && (
              <div>
                <h3>Experience</h3>
                {response.parsed_data.experience.map((exp, index) => (
                  <div key={index}>
                    <h4>{exp.position} at {exp.company}</h4>
                    <p>{exp.duration}</p>
                    <p>{exp.description}</p>
                    {exp.key_achievements && exp.key_achievements.length > 0 && (
                      <div>
                        <strong>Key Achievements:</strong>
                        <ul>
                          {exp.key_achievements.map((achievement, i) => (
                            <li key={i}>{achievement}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Skills */}
            {response.parsed_data?.skills && response.parsed_data.skills.length > 0 && (
              <div>
                <h3>Skills</h3>
                <ul>
                  {response.parsed_data.skills.map((skill, i) => (
                    <li key={i}>{skill}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Projects */}
            {response.parsed_data?.projects && response.parsed_data.projects.length > 0 && (
              <div>
                <h3>Projects</h3>
                {response.parsed_data.projects.map((proj, index) => (
                  <div key={index}>
                    <h4>{proj.name}</h4>
                    <p>{proj.description}</p>
                    {proj.technologies && proj.technologies.length > 0 && (
                      <p>
                        <strong>Technologies:</strong>{" "}
                        {proj.technologies.join(", ")}
                      </p>
                    )}
                    {proj.duration && <p><strong>Duration:</strong> {proj.duration}</p>}
                    {proj.url && <a href={proj.url} target="_blank" rel="noopener noreferrer">Project Link</a>}
                  </div>
                ))}
              </div>
            )}

            {/* Strengths */}
            {response.grading_result.strengths && response.grading_result.strengths.length > 0 && (
              <div>
                <h3>Strengths</h3>
                <ul>
                  {response.grading_result.strengths.map((strength, index) => (
                    <li key={index}>{strength}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Resume Improvement Tips */}
            {response.grading_result.tips && response.grading_result.tips.length > 0 && (
              <div>
                <h3>Resume Improvement Tips</h3>
                <ul>
                  {response.grading_result.tips.map((tip, index) => (
                    <li key={index}>{tip}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Detailed Feedback */}
            {response.grading_result.detailed_feedback && (
              <div>
                <h3>Detailed Feedback</h3>
                <p>{response.grading_result.detailed_feedback}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  )
}

export default App