import getopt, argparse
from plugins import Stats, ReadSupport, SplicedLengths, MergedInfo, SpliceSiteScoring
from src import Merge

"""
tmerge CLI
==========
Runs tmerge as a CLI with stats, read support, spliced lengths, merged info and splice site scoring plugins enabled.
"""
def main():
    description = "tmerge 2.0 Beta"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-i", "--input", help="Input GTF file")
    parser.add_argument("-o", "--output", help="Output GTF file")
    parser.add_argument("-s", "--stats", action="store_true", help="Provide statistics for merged transcripts.")
    parser.add_argument("--tolerance", help="Exon overhang tolerance", type=int, default=0)
    parser.add_argument("--min_read_support", help="Minimum read support", type=int, default=0)
    parser.add_argument("--end_fuzz", help="end fuzz", type=int, default=0)
    parser.add_argument("--speed", help="Speed mode. Enables options that forgoe sensitivity and precision for faster merge time.", action="store_true")
    parser.add_argument("--processes", help="The number of processes (threads) allowed to run. Must be greater than 2. If left unspecified, then will use the maximum number available.", type=int, default=None)
    parser.add_argument("--splice_scoring", action="store_true")
    parser.add_argument("--acceptor_path")
    parser.add_argument("--donor_path")
    parser.add_argument("--fasta_path")
    parser.add_argument("--valid_acceptor", type=int, default=4)
    parser.add_argument("--valid_donor", type=int, default=4)


    args = parser.parse_args()

    merger = Merge(args.input, args.output, args.tolerance, args.processes)

    """
    Load plugins
    ============
    Order matters here for speed. 
    Functions that tap into hooks are ran in the order they are tapped. I.e. the first one to tap, will be the first to execute.
    If plugins are removing transcripts than they should run early to reduce the search space.
    """
    plugins = [
        SpliceSiteScoring,
        ReadSupport,
        SplicedLengths,
        MergedInfo,
        Stats
    ]

    for p in plugins:
        p(merger.hooks, **vars(args))

    """
    Begin merging
    =============
    """
    merger.merge()

if __name__ == "main":
    main()