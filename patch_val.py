import os
import re

with open('frontend/src/components/PlantBuilder/ValidationPanel.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("h-56", "h-[30vh] max-h-[45vh]")
text = text.replace("h-10", "h-8")

old_render = """        return (
            <li 
                key={idx} 
                onClick={() => {
                    if (issue.node_id && onSelectNode) onSelectNode(issue.node_id);
                }}
                className={`p-2 rounded border cursor-pointer transition-colors ${bg} ${textClass}`}
            >
                <div className="flex items-start">
                    <Icon className="w-4 h-4 mr-2 flex-shrink-0 mt-0.5 opacity-80" />
                    <div className="flex-1">
                        <div className="flex justify-between items-start mb-0.5">
                            <span className="font-semibold text-xs tracking-wider">{issue.issue_code}</span>
                            {issue.node_id && (
                                <span className="flex items-center text-[9px] font-mono bg-industrial-900/50 px-1 py-0.5 rounded border border-industrial-700/50 hover:bg-industrial-700 transition-colors">
                                    <Target className="w-2.5 h-2.5 mr-1 opacity-50" />
                                    {issue.node_id}
                                </span>
                            )}
                        </div>
                        <div className="text-[12px] leading-snug mb-1 text-gray-200">{issue.message}</div>
                        {issue.engineering_reason && (
                            <div className="text-[10px] opacity-70 mb-0.5 border-l pl-2 border-current">
                                {issue.engineering_reason}
                            </div>
                        )}
                        {issue.suggested_resolution && (
                            <div className="text-[10px] font-medium opacity-90 mt-1">
                                Suggestion: {issue.suggested_resolution}
                            </div>
                        )}
                    </div>
                </div>
            </li>
        );"""

new_render = """        return (
            <li 
                key={idx} 
                onClick={() => {
                    if (issue.node_id && onSelectNode) onSelectNode(issue.node_id);
                }}
                className={`p-1.5 rounded border cursor-pointer transition-colors ${bg} ${textClass} text-[10px]`}
            >
                <div className="flex items-start">
                    <Icon className="w-3 h-3 mr-1.5 flex-shrink-0 mt-0.5 opacity-80" />
                    <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start">
                            <span className="font-bold tracking-wider truncate">{issue.issue_code}</span>
                            {issue.node_id && (
                                <span className="flex items-center text-[9px] font-mono ml-2">
                                    [{issue.node_id}]
                                </span>
                            )}
                        </div>
                        <div className="text-gray-200 mt-0.5 truncate">{issue.message}</div>
                        {issue.engineering_reason && (
                            <div className="opacity-70 truncate">
                                {issue.engineering_reason}
                            </div>
                        )}
                    </div>
                </div>
            </li>
        );"""

text = text.replace(old_render, new_render)

with open('frontend/src/components/PlantBuilder/ValidationPanel.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
