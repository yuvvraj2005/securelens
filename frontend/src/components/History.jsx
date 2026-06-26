import { useEffect, useState } from "react";

function History() {

    const [scans, setScans] = useState([]);

    useEffect(() => {

        fetch("http://127.0.0.1:8000/scans")
            .then((response) => response.json())
            .then((data) => setScans(data))
            .catch((error) => console.error(error));

    }, []);

    return (

        <div className="mt-10 w-full max-w-6xl">

            <h2 className="text-3xl font-bold mb-6">
                Scan History
            </h2>

            <div className="bg-slate-900 rounded-xl border border-slate-800">

                {scans.length === 0 ? (

                    <p className="p-6 text-slate-400">
                        No scans found.
                    </p>

                ) : (

                    scans.map((scan) => (

                        <div
                            key={scan.id}
                            className="flex justify-between items-center border-b border-slate-800 p-5"
                        >

                            <div>

                                <p className="font-semibold">
                                    {scan.target}
                                </p>

                                <p className="text-slate-400 text-sm">
                                    Scan #{scan.id}
                                </p>

                            </div>

                            <div className="text-right">

                                <p className="font-bold">
                                    Score {scan.score}
                                </p>

                            </div>

                        </div>

                    ))

                )}

            </div>

        </div>

    );

}

export default History;
