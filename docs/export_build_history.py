"""Export user/assistant text from an explicitly selected local Codex session.

Excludes instructions, internal reasoning, environment messages and raw tools.
Does not rewrite dialogue or claim to export a whole ChatGPT account.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def export(source, destination):
    messages=[]
    tools=[]
    excluded=Counter()
    for line in source.read_text(encoding='utf-8').splitlines():
        record=json.loads(line)
        if record.get('type')!='response_item':
            continue
        payload=record.get('payload',{})
        kind=payload.get('type')
        if kind in {'function_call','custom_tool_call'}:
            tools.append({'timestamp':record.get('timestamp'),'tool':payload.get('name','unknown')})
        if kind!='message':
            excluded[kind or 'unknown']+=1
            continue
        role=payload.get('role')
        if role not in {'user','assistant'} or payload.get('channel')=='analysis':
            excluded['non-public instruction/analysis message']+=1
            continue
        text='\n'.join(part['text'] for part in payload.get('content',[]) if part.get('type') in {'input_text','output_text'} and isinstance(part.get('text'),str))
        if text.lstrip().startswith('<environment_context>'):
            excluded['environment context message']+=1
            continue
        if text:
            messages.append({'timestamp':record.get('timestamp'),'role':role,'text':text})
    destination.mkdir(parents=True,exist_ok=True)
    serialized=json.dumps(messages,ensure_ascii=False,indent=2)+'\n'
    (destination/'conversation.json').write_bytes(serialized.encode('utf-8'))
    cutoff=messages[-1]['timestamp'] if messages else None
    header=(
        '# FINN — original user/assistant conversation\n\n'
        'This is a text export from the local Codex session used to build FINN. '
        'The dialogue preserves the source wording, spelling, order and timestamps. '
        'It includes the original requests, limitations, deployment troubleshooting and subsequent discussion; '
        'it has not been rewritten to improve the apparent process.\n\n'
        f'**Snapshot cutoff (UTC):** {cutoff}. Later messages are outside this snapshot.\n\n'
        '**Scope:** user/assistant text messages only. Environment-context messages, system/developer '
        'instructions, internal reasoning, tool arguments and raw tool outputs are excluded. '
        'Excluded technical records can contain unrelated local file listings or private runtime context. '
        'This is not a complete raw session log or an account-wide ChatGPT export. '
        'The JSON preserves text in a machine-readable form; the tool index lists invocation names '
        'and timestamps only. Test and deployment evidence is documented separately.\n\n---\n\n'
    )
    transcript=header+'\n\n---\n\n'.join(
        f"## {i}. {m['role'].title()} · {m['timestamp']}\n\n{m['text']}"
        for i,m in enumerate(messages,1)
    )+'\n'
    (destination/'conversation.md').write_text(transcript,encoding='utf-8')
    audit={
        'format':'Codex user/assistant text export, not a raw or account-wide export',
        'exported_at_utc':datetime.now(timezone.utc).isoformat(),
        'snapshot_cutoff_utc':cutoff,
        'message_count':len(messages),
        'roles':dict(Counter(m['role'] for m in messages)),
        'conversation_json_sha256':hashlib.sha256(serialized.encode('utf-8')).hexdigest(),
        'excluded_record_counts':dict(excluded),
        'tool_invocations':tools,
        'note':'No dialogue rewriting or message-specific redaction was performed. The hash checks this export file, not authenticity of an external source.'
    }
    (destination/'export-manifest.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Exported {len(messages)} messages; cutoff {cutoff}; SHA256 {audit["conversation_json_sha256"]}')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path,help='Explicitly chosen local Codex session JSONL file')
    parser.add_argument('--destination',type=Path,default=Path('docs/ai-build-history'))
    args=parser.parse_args()
    export(args.source,args.destination)
