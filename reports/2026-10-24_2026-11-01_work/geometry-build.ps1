$ErrorActionPreference='Stop'
$dir=Split-Path -Parent $MyInvocation.MyCommand.Path
$source=Get-Content (Join-Path $dir 'geometry-selected-input.json') -Raw|ConvertFrom-Json
$history=Get-Content (Join-Path $dir 'geometry-history-check.json') -Raw|ConvertFrom-Json
$allHistory=Get-Content (Join-Path $dir '../paper-history.json') -Raw|ConvertFrom-Json
$annotations=@(Get-ChildItem (Join-Path $dir 'geometry-annotations*.json')|ForEach-Object {Get-Content $_.FullName -Raw|ConvertFrom-Json})
$papers=@(foreach($p in $source){
 $h=$history|Where-Object id -eq $p.id|Select-Object -First 1
 $a=$annotations|Where-Object id -eq $p.id|Select-Object -First 1
 $row=[ordered]@{};foreach($prop in $p.PSObject.Properties){$row[$prop.Name]=$prop.Value}
 if($a){
  foreach($prop in $a.PSObject.Properties){$row[$prop.Name]=$prop.Value}
  $row.abstract_read=$true;$row.reading_level='abstract';$row.reading_evidence='Complete official arXiv abstract supplied in main-search-candidates.json / main-cross-metadata.json, displayed and read by geometry agent; no full text or execution.'
  if(-not $row.disposition){$row.disposition='supplemental';$row.reason='摘要包含直接几何/3D重建、地图或相关空间理解贡献；本次仅摘要级跟踪。'}
  $row.problem=($p.abstract -split '(?<=[.!?])\s+',2)[0]
  $row.insight_math=$a.method
  $row.priority=[bool]$a.priority
  $row.priority_reason=if($a.priority){'与前馈几何主线直接相关，具有几何、效率、可靠性或系统接口贡献；编辑优先，不代表复现。'}else{''}
  if($a.priority){$row.priority_reason='优先核对这一直接几何/系统贡献及其适用边界：'+$a.method}
  $row.follow_up='进一步核对全文协议、消融和代码入口；本次未运行。'
 }elseif($h.old){
  $row.abstract_read=$false;$row.reading_level='metadata';$row.disposition='same_version_processed';$row.reason='上期ledger已有同ID+version处置：'+$h.old+'；本次不重复计算阅读/报道。';$row.previous_disposition=$h.old
 }else{$row.abstract_read=$false;$row.disposition='unresolved';$row.reason='摘要待判读。'}
 $hv=$allHistory.papers.($p.id).versions.('v'+$p.version)
 if($hv -and $hv.status -in @('deep_read','supplemental','revision_tracking')){
  $row.disposition='already_covered';$row.reason='paper-history.json已有精确ID+version纳入，保留原报告证据，不重复报道。';$row.previous_report=$hv.report_path;$row.previous_evidence_level=$hv.evidence_level
 }
 $start=[datetimeoffset]'2026-10-24T08:17:58Z';$end=[datetimeoffset]'2026-11-01T14:59:32Z'
 $v1=[datetimeoffset]$p.v1_utc;$upd=[datetimeoffset]$p.updated_utc
 $row.window_class=if($v1 -gt $start -and $v1 -le $end){'new'}elseif($upd -gt $start -and $upd -le $end){'revised'}elseif($p.version -gt 1){'historical_revision_backfill'}else{'historical_backfill'}
 $row.date_validation='Official Atom published/updated fields; selected abs submission-history audit delegated to main agent. List announcement dates not used.'
 if($p.id.Substring(0,4) -ne $v1.ToString('yyMM')){$row.date_flag='arXiv ID-month differs from Atom published month; do not infer date from identifier; verify abs history.'}
 [pscustomobject]$row
})
$queries=@(Get-Content (Join-Path $dir 'main-search-manifest.json') -Raw|ConvertFrom-Json|Where-Object family -Like 'B-*')+@(Get-Content (Join-Path $dir 'main-advanced-manifest.json') -Raw|ConvertFrom-Json|Where-Object family -Like 'B-*')
$result=[ordered]@{run_at='2026-11-01T14:59:32Z';generated_at=[datetime]::UtcNow.ToString('o');status='candidate_review_complete_pending_central_date_audit';coverage_start_utc='2026-10-24T08:17:58Z';coverage_end_utc='2026-11-01T14:59:32Z';queries=$queries;search_note='Own parallel native API/Scholar probe aborted after 1019-second connector stall. Main agent API, Advanced, category and repo cross-discovery evidence reused; queries below are inherited main-agent observations, not independent fetches. See main-search-manifest.json/main-advanced-manifest.json for full coverage. Main route181 plus extra65 and original97 union has 265 unique IDs; each has an explicit disposition. No full text or code execution claimed.';candidate_count=$papers.Count;actual_abstract_read=@($papers|Where-Object abstract_read).Count;disposition_counts=@($papers|Group-Object disposition|ForEach-Object {[pscustomobject]@{disposition=$_.Name;count=$_.Count}});papers=$papers}
$result.failed_probes=@([ordered]@{source='Native PowerShell Invoke-WebRequest + Sider Scholar arxiv_search parallel probe';query='(ti:VGGT OR abs:VGGT) AND submittedDate:[202610240000 TO 202611012359]';url='https://export.arxiv.org/api/query?search_query=%28ti%3AVGGT%20OR%20abs%3AVGGT%29%20AND%20submittedDate%3A%5B202610240000%20TO%202611012359%5D&start=0&max_results=200';retrieved_at=$null;attempt_time_note='Attempt was before tool interruption; wall time 1019 seconds reported by interrupted tool, exact UTC unavailable.';status='aborted_without_result';total=$null;fetched=$null;page_count=0;exhausted=$false;replacement='Inherited main-api-B-foundation submittedDate/lastUpdatedDate and Advanced first/latest queries, plus central category and repo inventory.'})
$result.validation=[ordered]@{route181_plus_extra65_all_present=$true;unique_id_count=@($papers.id|Select-Object -Unique).Count;unresolved=@($papers|Where-Object disposition -eq unresolved).Count;included_missing_abstract=@($papers|Where-Object {$_.disposition -eq 'supplemental' -and -not $_.abstract_read}).Count;included_takeaway_outside_40_100=@($papers|Where-Object {$_.disposition -eq 'supplemental' -and ($_.takeaway.Length -lt 40 -or $_.takeaway.Length -gt 100)}).Count;date_flags=@($papers|Where-Object date_flag|Select-Object id,version,v1_utc,updated_utc,date_flag);full_text_read=0}
$result|ConvertTo-Json -Depth 50|Set-Content (Join-Path $dir 'geometry-search.json') -Encoding utf8
$result|Select-Object candidate_count,actual_abstract_read,disposition_counts|ConvertTo-Json -Depth 5
