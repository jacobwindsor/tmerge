from functools import reduce

class ReadSupport():
    """
    Computes read support for each transcript and filters transcripts that do not meet min_abundance.

    abundance: read support as a fraction of the maximum read support in a contig.

    Parameters
    ----------
    hooks: dict
    end_fuzz: int
        Tolerated fuzziness of 5' and 3' ends for two reads to be considered equivalent when computing read support
    min_abundance: float
        Minimum abundance for a transcript. Any transcripts with abundance below this threshold will be removed.
    """
    def __init__(self, hooks, end_fuzz = 0, min_abundance = 0.15, **kwargs):
        if min_abundance > 1:
            raise TypeError("min_abundance must be < 1.")

        self.end_fuzz = end_fuzz
        self.min_abundance = min_abundance

        hooks["transcript_added"].tap(self.add_meta)
        hooks["contig_built"].tap(self.calc_support)

    def add_meta(self, transcript):
        transcript.meta["read_support"] = 1
        transcript.meta["abundance"] = 0

    def supports_target(self, target, other):
        if (
            other.junctions == target.junctions and 
            other.TSS >= target.TSS - self.end_fuzz and
            other.TSS <= target.TSS + self.end_fuzz and
            other.TES >= target.TES - self.end_fuzz and
            other.TES <= target.TES + self.end_fuzz
        ):
            return True
        
        return False 

    def calc_support(self, transcripts):
        max_read_support = 1
        for i, target in enumerate(transcripts):
            if  target.removed:
                continue
            
            for other in transcripts[i+1:]:
                if other.TSS - self.end_fuzz > target.TSS:
                    # Since input is ordered, can break early if other comes after target
                    break
                
                if other.removed:
                    continue
                
                if self.supports_target(target, other):
                    target.meta["read_support"] += 1
                    other.remove() # Remove if supports target as is the same TM

            if target.meta["read_support"] > max_read_support:
                max_read_support = target.meta["read_support"]

        for t in transcripts:
            t.meta["abundance"] = t.meta["read_support"] / max_read_support
            if t.meta["abundance"] < self.min_abundance:
                t.remove()
