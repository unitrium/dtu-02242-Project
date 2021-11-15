from typing import Dict
from Parser.program_graph import Edge, ProgramGraph


class AbstractAnalysis:
    @staticmethod
    def merge(mapping1: Dict, mapping2: Dict) -> Dict:
        """Merge two mappings."""
        if mapping2 == "undef" and not mapping1 == "undef":
            return mapping1
        elif mapping2 == "undef" and mapping1 == "undef":
            return "undef"
        elif mapping1 == "undef":
            return mapping2

    @staticmethod
    def included(mapping1: Dict, mapping2: Dict) -> bool:
        """Checks if the mapping1 is included in the mapping 2."""
        if mapping2 == "undef":
            return False
        if mapping1 == "undef":
            return True

    @staticmethod
    def init_mapping(programGraph: ProgramGraph) -> Dict:
        """Initializes the mapping according to the analysis."""
        pass

    @staticmethod
    def update_mapping(mapping: Dict, edge: Edge) -> Dict:
        """Update the mapping based on the kill/gen functions of the analysis."""
        if mapping == "undef":
            return mapping

    @staticmethod
    def copy_mapping(mapping: Dict) -> Dict:
        """Returns a deep copy of a mapping."""
        if mapping == "undef":
            return mapping

    @staticmethod
    def reverse() -> bool:
        return False
