import { useEffect, useState } from 'react'
import './App.css'



function App() {
  type systemStatus = "loading" | "readyForInput" | "readyForOutput" | "initializationError" | "processing" | "inputTypeError" | "inputError";
  const [systemReady, setSystemReady] = useState<systemStatus>("loading");

  const apiUrl: string = import.meta.env.API_URL || "http://localhost:8000";
  useEffect(() => { 
    const fetchStatus = async () => {
      try {
        const response: any = await fetch(`${apiUrl}/status`, { method: "GET" });
        const data: any = await response.json();
        const status: systemStatus = data.status;
        setSystemReady(status);
      } catch (error) {
        console.error("Error fetching system status:", error);
        setSystemReady("initializationError");
      }
    };
    fetchStatus();
  }, []);

  const handleFileSubmission = async (event: React.FormEvent<HTMLFormElement>) => {
    setSystemReady("processing");
    event.preventDefault();
    const formData: FormData = new FormData(event.currentTarget);
    console.log("Form data submitted:", formData.get("fileInput"));
    try {
      var response: Response | null = null;
      const graphFile = (formData.get("graphFileInput") as File);
      const textFile = (formData.get("textFileInput") as File);

      const hasGraphFile = graphFile && graphFile instanceof File && graphFile.size > 0;
      const hasTextFile = textFile && textFile instanceof File && textFile.size > 0;

      if (!hasGraphFile && !hasTextFile) {
        alert("Please upload at least one file.");
        setSystemReady("readyForInput");
        return;
      } else if (!hasGraphFile) {
        response = await fetch(`${apiUrl}/initialize_only_text`, {
          method: "POST",
          body: formData,
        });
      } else if (!hasTextFile) {
        response = await fetch(`${apiUrl}/initialize_only_graph`, {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch(`${apiUrl}/initialize_both`, {
          method: "POST",
          body: formData,
        });
      }
      
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const data: any = await response.json();
      setSystemReady(data.status);
    } catch (error) {
        console.error("Error submitting file:", error);
        setSystemReady("inputError");  
      }
}

  if(systemReady === "loading") {
    return (
      <>
        <p style={{"fontSize": "50px"}}> Loading ...</p>
      </>
    )
  } else if(systemReady === "processing") {
    return (
      <>
        <p style={{"fontSize": "50px"}}> Processing input ...</p>
      </>
    )
  
  } else if(systemReady === "inputTypeError"){
    return (
      <>
        <p style={{"fontSize": "50px"}}>The structure of your input file is not proper</p>
        <p style={{"fontSize": "40px"}}>Please change the structure and resubmit your file</p>
        <button onClick={() => setSystemReady("readyForInput")}>Go back to Mainpage</button>
      </>
    )
  }else if(systemReady === "inputError"){
    return (
      <>
        <p style={{"fontSize": "50px"}}> Submission Error </p>
        <button onClick={() => setSystemReady("readyForInput")}>Go back to Mainpage</button>
      </>
    )
  }else if(systemReady === "readyForInput") {
    return (
    <>
      <h1> Welcome to the Recommendation System Application</h1>
      <p> This application allows you to get recommendations based on your input.</p>
      <p> Please upload a file using the box below (accepted file types: .csv/.txt) and click on the "Initialize System" </p>
      <form method="post" encType="multipart/form-data" onSubmit={handleFileSubmission} className="submissionForm">
        <div style={{"display": "flex", "flexDirection": "column", "gap": "10px", marginLeft: "25%"}}>
          <div style={{"display": "flex", "flexDirection": "row", "gap": "10px"}}>
            <label htmlFor="graphFileInput">Upload Click File: </label>
            <input type="file" id="graphFileInput" name="graphFileInput" accept=".csv, .txt" />
          </div>
          <div style={{"display": "flex", "flexDirection": "row", "gap": "10px"}}>
            <label htmlFor="textFileInput">Upload Description File: </label>
            <input type="file" id="textFileInput" name="textFileInput" accept=".csv, .txt" />
          </div>
        </div>
        <div style={{marginRight: "25%"}}>
          <button type="submit"> Initialize System</button>  
        </div>
         
      </form>
    </>
    )
  } else if(systemReady === "readyForOutput") {
  
  } else if(systemReady === "initializationError") {
    return (
      <>
        <p style={{"color": "red", "fontSize": "30px"}}> Error: Unable to connect to the server. Please check your connection or try again later.</p>
      </>
    )
  }
}

export default App
