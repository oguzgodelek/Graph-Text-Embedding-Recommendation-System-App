import { useEffect, useState } from 'react'
import './App.css'
import {type Status, type ItemResponse, type CollectionResponse, type Item} from './DataTypes.ts'

const itemCount: number = 20;

function App(){
  const [systemStatus, setSystemStatus] = useState<Status>("loading");
  const [availableCollections, setAvailableCollections] = useState<string[]>([]);
  const [selectedCollection, setSelectedCollection] = useState<string>("");
  const [itemList, setItemList] = useState<Item[]>([]);

  const apiUrl: string = import.meta.env.API_URL || "http://localhost:8000";
  useEffect(() => { 
    const fetchStatus = async () => {
      try {
        const response: Response = await fetch(`${apiUrl}/status`, { method: "GET" });
        const data: any = await response.json();
        const status: Status = data.status;
        setSystemStatus(status);
      } catch (error) {
        console.error("Error fetching system status:", error);
        setSystemStatus("initializationError");
      }
    };
    fetchStatus();
  }, []);

  useEffect(() => {
    const fetchCollections = async () => {
      try {
        const response: Response = await fetch(`${apiUrl}/available_collections`, { method: "GET" });
        const data: CollectionResponse = await response.json();
        const collections: string[] = data.collectionList;
        setAvailableCollections(collections);
      } catch (error) {
        console.error("Error fetching available databases:", error);
        setSystemStatus("initializationError");
      }
      
    };

    if (systemStatus === "readyForOutput") {
      fetchCollections();
    }
  }, [systemStatus]);

  useEffect(() => {
    const fetchItems = async (): Promise<void> => {
      try {
        const response: Response = await fetch(`${apiUrl}/retrieve_random/${itemCount}/${selectedCollection}`)
        const data: ItemResponse = await response.json();
        const items: Item[] = data.itemList;
        setItemList(items);
      } catch (error) {
        console.error("Error fetching available databases:", error);
        setSystemStatus("initializationError");
      }

    };

    if (systemStatus === "search") {
      fetchItems();
    }else {
        setSystemStatus("initializationError");
    }

  }, [selectedCollection]);

  const handleFileSubmission = async (event: React.FormEvent<HTMLFormElement>) => {
    alert("File submission started");
    setSystemStatus("entrypoint");
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
        setSystemStatus("readyForInput");
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
      
      const data: any = await response.json();
      alert("Output is ready: " + data.collection_name);
      
    } catch (error) {
        console.error("Error submitting file:", error);
        setSystemStatus("inputError");
      }
}

  if(systemStatus === "loading") {
    return (
      <>
        <p style={{"fontSize": "50px"}}> Loading ...</p>
      </>
    )
  } else if(systemStatus === "processing") {
    return (
      <>
        <p style={{"fontSize": "50px"}}> Processing input ...</p>
      </>
    )
  
  } else if(systemStatus === "inputTypeError"){
    return (
      <>
        <p style={{"fontSize": "50px"}}>The structure of your input file is not proper</p>
        <p style={{"fontSize": "40px"}}>Please change the structure and resubmit your file</p>
        <button onClick={() => setSystemStatus("readyForInput")}>Go back to Mainpage</button>
      </>
    )
  }else if(systemStatus === "inputError"){
    return (
      <>
        <p style={{"fontSize": "50px"}}> Submission Error </p>
        <button onClick={() => setSystemStatus("readyForInput")}>Go back to Mainpage</button>
      </>
    )
  }else if(systemStatus === "entrypoint") {
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
                  onClick={() => setSystemStatus("readyForOutput")}>
            Select Initialized Database
          </button>  
          <button type="submit" 
                  onClick={() => setSystemStatus("readyForInput")}>
            Submit New Data
          </button> 
        </div>
      </>
    )
    
  }
  else if(systemStatus === "readyForInput") {
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
    <button style={{ marginTop: "50px" }} onClick={() => setSystemStatus("entrypoint")}>Back</button>
  </>
);
  } else if(systemStatus === "readyForOutput") {
    return (
      <>
        <h1> Select an Initialized Database</h1>
        <p> You can select an initialized database to get recommendations.</p>
        <p> Please select a database from the list below:</p>
        <div style={{ marginRight: "33%", marginLeft: "33%", flexDirection: "column", display: "flex", rowGap: "10px" }}>
          {availableCollections.length > 0 ? (
            availableCollections.map((db, index) => (
              <button key={index} onClick={(): void => {setSelectedCollection(db); setSystemStatus("search");  }}>
                {db}
              </button>
            ))
          ) : (
            <div>
              <p>No databases available. </p>
              <p>Please initialize a database first.</p>
            </div>
          )}
          <button onClick={() => setSystemStatus("entrypoint")}>Back</button>
        </div>
      </>
    )
  } else if(systemStatus === "search"){
    return (
        <>
            <table className="table-auto border-collapse border border-gray-300 w-full">
      <thead>
      <tr className="bg-gray-200">
          <th className="border border-gray-300 px-4 py-2">ID</th>
          <th className="border border-gray-300 px-4 py-2">Name</th>
          <th className="border border-gray-300 px-4 py-2">Description</th>
          <th className="border border-gray-300 px-4 py-2">Select</th>
      </tr>
      </thead>
                <tbody>
                {itemList.map((item: Item) => (
                    <tr key={item.id}>
                        <td className="border border-gray-300 px-4 py-2">{item.id}</td>
                        <td className="border border-gray-300 px-4 py-2">{item.name}</td>
                        <td className="border border-gray-300 px-4 py-2">{item.description}</td>
                        <td className="border border-gray-300 px-4 py-2"><button onClick={async (): Promise<void> => {
                            try {
                                const response: Response = await fetch(`${apiUrl}/retrieve_similar/${itemCount}/${selectedCollection}/${item.id}`)
                                const data: ItemResponse = await response.json();
                                const items: Item[] = data.itemList;
                                setItemList(items);
                            } catch (error) {
                                console.error("Error fetching available databases:", error);
                                setSystemStatus("initializationError");
                             }
                        }}> Select </button></td>
                    </tr>
                ))}
                </tbody>
            </table>
            <button onClick={() => setSystemStatus("readyForOutput")}>Back</button>
        </>
    )
  } else if (systemStatus === "initializationError") {
      return (
      <>
        <p style={{"color": "red", "fontSize": "30px"}}> Error: Unable to connect to the server. Please check your connection or try again later.</p>
      </>
    )
  }
}

export default App
