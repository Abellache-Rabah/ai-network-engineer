import logging
import tempfile
import os
import shutil
from typing import List, Dict, Any, Optional
from pybatfish.client.session import Session
# from pybatfish.datamodel import Answer
from pybatfish.datamodel.flow import HeaderConstraints

# Configure logging
logging.getLogger("pybatfish").setLevel(logging.WARN)

class BatfishConnector:
    def __init__(self, host: str = "localhost", ssl: bool = False):
        self.host = host
        self.ssl = ssl
        self.bf = Session(host=host, ssl=ssl)

    def verify_config(self, config_content: str, filename: str = "config.cfg", platform: str = "cisco") -> Dict[str, Any]:
        """
        Uploads a single configuration file to Batfish and runs initialization checks.
        Returns a dictionary with parsing results and any issues found.
        """
        # Create a temporary directory for the snapshot
        with tempfile.TemporaryDirectory() as temp_dir:
            configs_dir = os.path.join(temp_dir, "configs")
            os.makedirs(configs_dir)
            
            # Write the config file
            with open(os.path.join(configs_dir, filename), "w") as f:
                f.write(config_content)
            
            # Initialize snapshot
            snapshot_name = f"snap_{os.urandom(4).hex()}"
            try:
                self.bf.init_snapshot(temp_dir, name=snapshot_name, overwrite=True)
                
                # Get init issues (parsing errors, warnings)
                # Parse warning status
                parse_status = self.bf.q.fileParseStatus().answer().frame()
                
                # Get specific parsing issues if any
                init_issues = self.bf.q.initIssues().answer().frame()
                
                # Simplify results for consumption
                results = {
                    "status": "success",
                    "parse_status": parse_status.to_dict(orient="records"),
                    "issues": init_issues.to_dict(orient="records"),
                    "snapshot": snapshot_name
                }
                
                return results

            except Exception as e:
                return {
                    "status": "error",
                    "message": str(e)
                }
            finally:
                # Cleanup snapshot if needed, though pybatfish might keep it references
                pass

    def get_undefined_references(self) -> List[Dict[str, Any]]:
        """
        Checks for undefined references in the current snapshot
        """
        try:
            return self.bf.q.undefinedReferences().answer().frame().to_dict(orient="records")
        except Exception:
            return []
