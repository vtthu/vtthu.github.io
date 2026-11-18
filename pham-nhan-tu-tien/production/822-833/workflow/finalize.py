from pathlib import Path
import json, hashlib, subprocess, zipfile, re, shutil
from datetime import datetime, timezone
from PIL import Image
import fitz

repo=Path('/tmp/comic-publish-822'); root=repo/'pham-nhan-tu-tien'
work=Path('/workspace/comic-batch-822-833'); out=root/'production/822-833'
base='afa372b1ae81a0daa2fd93f52fe4c08272a14f62'
def git(*args): return subprocess.check_output(['git',*args],cwd=repo,text=True).strip()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
out.mkdir(parents=True,exist_ok=True)
sources=json.loads((work/'sources.json').read_text()); records=[]
for n in range(822,834):
    cfg=json.loads((work/f'{n}.json').read_text()); count=len(cfg['images'])
    assert count in (4,5)
    dest=root/f'chapters/{n}'; pages=sorted(dest.glob('trang-*.png'))
    assert len(pages)==count
    src=Path(sources[str(n)]).read_bytes()
    assert src==(dest/'SOURCE.txt').read_bytes()==(work/f'CHUONG {n}.txt').read_bytes()
    imgs=[]
    for i,p in enumerate(pages,1):
        assert p.name==f'trang-{i:02}.png'
        with Image.open(p) as im: im.verify()
        with Image.open(p) as im: im.load(); assert im.size==(1055,1492)
        imgs.append({'file':p.name,'pixels':[1055,1492],'sha256':sha(p)})
    with fitz.open(dest/f'chuong-{n}.pdf') as pdf:
        assert len(pdf)==count
        assert all(abs(p.rect.width-595.2756)<.1 and abs(p.rect.height-841.8898)<.1 for p in pdf)
    for m in cfg['models']:
        with Image.open(root/'models'/m) as im: im.verify()
    with zipfile.ZipFile(f'/tmp/comic-batch-822-833/truyen-tranh-chuong-{n}.zip') as z:
        assert z.testzip() is None
    commit=git('log','-1','--format=%H','--',f'pham-nhan-tu-tien/chapters/{n}')
    assert commit!=base
    subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],cwd=repo,check=True)
    records.append({'chapter':n,'title':cfg['title'],'status':'completed','pages':count,'chapter_commit':commit,'source_sha256':hashlib.sha256(src).hexdigest(),'source_bytes':len(src),'models':cfg['models'],'continuity_notes':cfg['notes'],'pngs':imgs})
changed=git('diff','--name-only',base,'HEAD').splitlines()
assert all(p.startswith('pham-nhan-tu-tien/') for p in changed)
assert not git('diff','--diff-filter=MD','--name-only',base,'HEAD','--','pham-nhan-tu-tien/models')
new_models=git('diff','--diff-filter=A','--name-only',base,'HEAD','--','pham-nhan-tu-tien/models').splitlines()
models=[]
for name in new_models:
    p=repo/name
    with Image.open(p) as im: im.verify()
    models.append({'path':str(Path(name).relative_to('pham-nhan-tu-tien')),'sha256':sha(p)})
mf=root/'ARCHIVE_MANIFEST.json'; data=json.loads(mf.read_text())
entries={e['path']:e for e in data['files']}
old=json.loads(git('show',base+':pham-nhan-tu-tien/ARCHIVE_MANIFEST.json'))
assert {e['path'] for e in old['files']}.issubset(entries)
assert {e['chapter'] for e in old['chapters']}.issubset({e['chapter'] for e in data['chapters']})
for r in records:
    assert len([x for x in data['chapters'] if x['chapter']==r['chapter'] and x['pages']==r['pages']])==1
total=sum(r['pages'] for r in records)
assert not git('diff','--name-only',base,'HEAD','--','pham-nhan-tu-tien/chapters/807','pham-nhan-tu-tien/production/in-progress/807')
report={'status':'completed','verified_at_utc':datetime.now(timezone.utc).isoformat(),'chapters':12,'PNG_pages':total,'PDFs_A4':12,'pages_per_chapter':[4,5],'PNG_pixels':[1055,1492],'source_identical_to_user_uploads':True,'PDF_page_counts_and_A4_verified':True,'all_PNG_decodes_verified':True,'ZIP_integrity_verified_locally':True,'root_website_untouched':True,'existing_model_files_unchanged':True,'old_archive_paths_and_chapter_records_preserved':True,'new_model_images':models}
(out/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(out/'CHAPTER_REGISTRY.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
continuity=(work/'CONTINUITY.txt').read_text()
style=(work/'STYLE_GUIDE.md').read_text()
(out/'STYLE_GUIDE.md').write_text(style)
text=f'# Chương 822–833 — hoàn thành\n\n**12 chương · {total} trang PNG riêng · 12 PDF A4 dọc.** Theo thứ tự tăng dần từ các TXT đính kèm, mỗi chương 4–5 trang. Từng chương được đẩy lên GitHub khi hoàn thành.\n\n| Chương | Tên | Trang | Ảnh truyện | PDF | Commit |\n|---|---|---:|---|---|---|\n'
for r in records:
    n=r['chapter']; c=r['chapter_commit']
    text+=f"| {n} | {r['title']} | {r['pages']} | [Đọc truyện](../../chapters/{n}/README.md) | [PDF A4](../../chapters/{n}/chuong-{n}.pdf) | [{c[:7]}](https://github.com/vtthu/vtthu.github.io/commit/{c}) |\n"
text+='\n[Model tham chiếu](../../models/) · [Bộ nhớ dự án](../../PROJECT_MEMORY.md) · [Bộ nhớ nhân vật](../../CHARACTER_MEMORY.md) · [Nguồn và commit](CHAPTER_REGISTRY.json) · [Kiểm tra kỹ thuật](VERIFICATION.json) · [Quy tắc hình ảnh](STYLE_GUIDE.md)\n\n'+continuity+'\n'
(out/'README.md').write_text(text)
(out/'workflow').mkdir(exist_ok=True)
for name in ['package.py','finalize.py','SOURCE_PLAN.md','CONTINUITY.txt']: shutil.copy2(work/name,out/'workflow'/name)
state=json.loads((work/'STATE.json').read_text())
(out/'workflow/image_result_save.js').write_text(state['stores']['save822']+'\n')
rd=root/'README.md'; s=rd.read_text();s=re.sub(r'## Đợt mới nhất: chương ([^\n]+)',r'## Đợt chương \1',s)
s=s.replace('\n\n',f'\n\n## Đợt mới nhất: chương 822–833\n\n[Đọc lần lượt 12 chương](production/822-833/README.md): **{total} trang PNG, 12 PDF A4**, đã đẩy từng chương.\n\n',1);rd.write_text(s)
note=f'\n\n## Hoàn thành đợt 822–833\n12 chương, {total} PNG, 12 PDF A4; mỗi chương 4–5 trang. Đẩy riêng từng chương theo yêu cầu. Mục lục production/822-833/README.md.\n\n'+continuity+'\n\n'+style+'\nModel mới:\n'+'\n'.join('- '+m['path'] for m in models)+'\n'
for name in ['PROJECT_MEMORY.md','CHARACTER_MEMORY.md']:
    p=root/name
    if '## Hoàn thành đợt 822–833' not in p.read_text(): p.open('a').write(note)
for p in [out/'README.md']+[root/f'chapters/{n}/README.md' for n in range(822,834)]:
    for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if not link.startswith(('https:','http:','#')): assert (p.parent/link).exists(),(p,link)
for p in root.rglob('*'):
    if p.is_file() and p!=mf:
        rel=str(p.relative_to(root));entries[rel]={'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)}
data['files']=[entries[k] for k in sorted(entries)];mf.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='new_model_images'},ensure_ascii=False));print('new_models',len(models))
