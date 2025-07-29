import { useEffect, useState } from 'react'
import './App.css'



function App() {
  type systemStatus = "loading" | "entrypoint" | "readyForInput" | "readyForOutput" | "initializationError" | "processing" | "inputTypeError" | "inputError" | "search";
  const [systemReady, setSystemReady] = useState<systemStatus>("loading");
  const [availableDatabases, setAvailableDatabases] = useState<string[]>([]);

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

  useEffect(() => {
    const fetchDatabases = async () => {
      try {
        const response: any = await fetch(`${apiUrl}/available_databases`, { method: "GET" });
        const data: any = await response.json();
        const databases: string[] = data.databases;
        setAvailableDatabases(databases);
      } catch (error) {
        console.error("Error fetching available databases:", error);
        setSystemReady("initializationError");
      }
      
    };

    if (systemReady === "readyForOutput") {
      fetchDatabases();
    }
  }, [systemReady]);

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
  }else if(systemReady === "entrypoint") {
    return (
      <>
        <h1> Welcome to the Recommendation System Application</h1>
        <p> This application allows you to get recommendations based on your inputs.</p>
        <p> You can upload description text or relation graph or both to initialize a recommendation session.</p>
        <div style={{marginRight: "33%", 
                     marginLeft: "33%", 
                     flexDirection: "column", 
                     display: "flex", 
                     rowGap: "10px"}}>
          <button style={{}} 
                  type="submit" 
                  onClick={() => setSystemReady("readyForOutput")}> 
            Select Initialized Database
          </button>  
          <button type="submit" 
                  onClick={() => setSystemReady("readyForInput")}> 
            Submit New Data
          </button> 
        </div>
      </>
    )
    
  }
  else if(systemReady === "readyForInput") {
    return (
  <>
    <p>
      Please upload a file using the box below (accepted file types: .csv/.txt) and click on the "Initialize System"
    </p>
    <p>You can upload a graph file, a text file or both.</p>
    <form
      method="post"
      encType="multipart/form-data"
      onSubmit={handleFileSubmission}
      className="submissionForm"
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "15px",
          marginLeft: "20%",
          marginRight: "10%",
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "row",
            alignItems: "center", // ensures vertical alignment
            gap: "10px",
            flexWrap: "nowrap", // prevents wrapping
          }}>
          <label htmlFor="graphFileInput" style={{ whiteSpace: "nowrap" }}>
            Upload Click File:
          </label>
          <input
            type="file"
            id="graphFileInput"
            name="graphFileInput"
            accept=".csv, .txt"
            style={{ flex: 1 }}
          />
        </div>

        <div
          style={{
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
            gap: "10px",
            flexWrap: "nowrap",
          }}
        >
          <label htmlFor="textFileInput" style={{ whiteSpace: "nowrap" }}>
            Upload Description File:
          </label>
          <input
            type="file"
            id="textFileInput"
            name="textFileInput"
            accept=".csv, .txt"
            style={{ flex: 1 }}
          />
        </div>
      </div>
      <div style={{ marginRight: "25%", marginTop: "20px" }}>
        <button type="submit">Initialize System</button>
      </div>
    </form>
    <button style={{ marginTop: "50px" }} onClick={() => setSystemReady("entrypoint")}>Back</button>
  </>
);
  } else if(systemReady === "readyForOutput") {
    return (
      <>
        <h1> Select an Initialized Database</h1>
        <p> You can select an initialized database to get recommendations.</p>
        <p> Please select a database from the list below:</p>
        <div style={{ marginRight: "33%", marginLeft: "33%", flexDirection: "column", display: "flex", rowGap: "10px" }}>
          {availableDatabases.length > 0 ? (
            availableDatabases.map((db, index) => (
              <button key={index} onClick={() => setSystemReady("search")}>
                {db}
              </button>
            ))
          ) : (
            <div>
              <p>No databases available. </p>
              <p>Please initialize a database first.</p>
            </div>
          )}
          <button onClick={() => setSystemReady("entrypoint")}>Back</button>
        </div>
      </>
    )
  } else if(systemReady === "search"){

  }else if(systemReady === "initializationError") {
    return (
      <>
        <p style={{"color": "red", "fontSize": "30px"}}> Error: Unable to connect to the server. Please check your connection or try again later.</p>
      </>
    )
  }
}

export default App
