import History from "./components/History";
import { useState } from "react";

import {
  Server,
  Lock,
  AlertTriangle,
  Network
} from "lucide-react";

function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleScan = async () => {
    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/scan",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url,
          }),
        }
      );

      const data = await response.json();

      setResult(data);
    } catch (error) {
      console.error(error);
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col items-center p-10">

      <h1 className="text-6xl font-bold mb-2">
        SecureLens
      </h1>

      <p className="text-slate-400 mb-10">
        Website Security Scanner
      </p>

      <div className="flex gap-3 w-full max-w-xl">

        <input
          className="flex-1 rounded-lg bg-slate-900 border border-slate-700 px-4 py-3"
          placeholder="github.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />

        <button
          onClick={handleScan}
          className="bg-blue-600 hover:bg-blue-700 px-5 py-3 rounded-lg"
        >
          {loading ? "Scanning..." : "Scan"}
        </button>

      </div>

      {result && (
        <>

          {/* Score Cards */}

          <div className="mt-10 grid grid-cols-3 gap-4 w-full max-w-4xl">

            <div className="bg-slate-900 border border-green-500/30 p-6 rounded-xl">
              <h3 className="text-slate-400">
                Score
              </h3>
              <p className="text-4xl font-bold">
                {result.result.score.overall_score}
              </p>
            </div>

            <div className="bg-slate-900 border border-blue-500/30 p-6 rounded-xl">
              <h3 className="text-slate-400">
                Grade
              </h3>
              <p className="text-4xl font-bold">
                {result.result.score.grade}
              </p>
            </div>

            <div className="bg-slate-900 border border-red-500/30 p-6 rounded-xl">
              <h3 className="text-slate-400">
                Risk
              </h3>
              <p className="text-4xl font-bold">
                {result.result.score.risk_level}
              </p>
            </div>

          </div>

          {/* SSL Information */}

          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-4xl">

  	    <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">

    		<div className="flex items-center gap-2 mb-4">
      		  <Lock size={22} />
      		  <h2 className="text-xl font-bold">
        	    SSL Information
      		  </h2>
    		</div>

    		<p>Issuer: {result.result.ssl.issuer}</p>
    		<p>Subject: {result.result.ssl.subject}</p>
    		<p>Expires On: {result.result.ssl.expires_on}</p>
    		<p>Days Remaining: {result.result.ssl.days_remaining}</p>

  	    </div>

  	    <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">

    	      <div className="flex items-center gap-2 mb-4">
      		<Server size={22} />
     	 	<h2 className="text-xl font-bold">
        	  Technology Detection
      		</h2>
    	      </div>

    	      <p>Server: {result.result.technology.server}</p>
    	      <p>Framework: {result.result.technology.framework}</p>
    	      <p>CDN: {result.result.technology.cdn}</p>

  	    </div>

	  </div>

          {/* Open Ports */}

          <div className="mt-6 w-full max-w-4xl">
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">

              <div className="flex items-center gap-2 mb-4">
  		<Network size={22} />
  		<h2 className="text-xl font-bold">
    		  Open Ports
  		</h2>
	       </div>

              {result.result.nmap.open_ports.length === 0 ? (
                <p>No open ports detected</p>
              ) : (
                result.result.nmap.open_ports.map(
                  (port, index) => (
                    <div
                      key={index}
                      className="border-b border-slate-700 py-2"
                    >
                      <strong>
                        {port.port}
                      </strong>
                      {" - "}
                      {port.service}
                      {" - "}
                      {port.version}
                    </div>
                  )
                )
              )}

            </div>
          </div>

          {/* Security Findings */}

          <div className="mt-6 mb-10 w-full max-w-4xl">
            <div className="bg-slate-900 p-6 rounded-xl">

              <div className="flex items-center gap-2 mb-4">
  		<AlertTriangle size={22} />
  		<h2 className="text-xl font-bold">
    		  Security Findings
  		</h2>
	      </div>

              {result.result.headers.findings.length === 0 ? (
                <p className="text-green-400">
                  ✅ No security issues found
                </p>
              ) : (
                result.result.headers.findings.map(
                  (finding, index) => (
                    <div
                      key={index}
                      className="border-b border-slate-700 py-3"
                    >
                      <span
  			className={
    			  finding.severity === "High"
      			    ? "text-red-400 font-bold"
      			    : finding.severity === "Medium"
      			    ? "text-orange-400 font-bold"
      			    : "text-yellow-400 font-bold"
  			}	
		       >
  			{finding.severity}
		       </span>

                      <p>
                        {finding.title}
                      </p>

                      <p className="text-slate-400 text-sm">
                        {finding.description}
                      </p>
                    </div>
                  )
                )
              )}

            </div>
          </div>

        </>
      )}

      <History />

    </div>
  );
}

export default App;
