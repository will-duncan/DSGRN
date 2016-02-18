#ifndef PATTERNMATCH_HPP
#define PATTERNMATCH_HPP

#include "DataStructures.hpp"
#include <algorithm>
#include <iostream>
#include <stack>

class PatternMatch {
	
	public:
		typedef std::list<std::pair<patternvector,uint64_t>> resultslist; // list< pair < pattern, number_matches > >
		typedef std::pair<uint64_t,uint64_t> node; // data type for stack, < wall_index, pattern_len > 
		typedef std::vector<std::pair<std::vector<uint64_t>,std::vector<uint64_t>>> memoize; // indexed by pattern length, first vector is wall_index, second is count

		// constructor
		PatternMatch ( wallgraphvector& wg ) : wallgraph(wg) {}

		/* loop over patterns; patterns are either already sorted in reverse order, or the input should be a partial order; can I do sorting during construction from a partial order? start at tail? (topological sorting)
		findoption == 1 -> find at most one match over all patterns (check subset of patterns)
		findoption == 2 -> find at most one match per pattern (check all patterns)
		findoption == 3 -> find number of matches for every pattern (check all patterns)
		*/
		resultslist patternMatch ( std::list<patternvector> allpatterns, const int findoption ); 
		
	private:
		const wallgraphvector& wallgraph;

		void _pruneRegister( patternvector newpattern, patternvector oldpattern, memoize& keepcount );
		uint64_t _patternMatch ( const patternvector pattern, const int findoption, memoize& keepcount );
		bool _checkForWordInLabels( const std::string word, const std::vector<std::set<char>> labels);
		void _addToStack ( const uint64_t newpatternlen, const node thisnode, memoize& keepcount, std::stack<node>& nodes_to_visit );
};

#endif
