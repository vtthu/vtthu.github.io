from pathlib import Path
import json, hashlib, subprocess, zipfile, shutil
from datetime import datetime, timezone
from PIL import Image
import fitz

repo=Path('/workspace/github-comic-backup')
root=repo/'pham-nhan-tu-tien'
work=Path('/workspace/comic-batch-559-569')
out=root/'production/559-569'
out.mkdir(parents=True,exist_ok=True)
(out/'workflow').mkdir(exist_ok=True)
expected={n:(5 if n in (561,562) else 4) for n in range(559,570)}
uploaded=json.loads((work/'sources.json').read_text())
report={'status':'completed','chapters':[],'total_pages':0,'total_pdfs':0,'source_files_byte_identical':True,'png_decode_and_portrait_A4':True,'pdf_A4_pages_verified':True,'chapter_ZIPs_verified_locally':True,'new_model_images':[]}
records=[]
all_models=set()
for n,count in expected.items():
    cfg=json.loads((work/f'{n}.json').read_text())
    d=root/f'chapters/{n}'
    pngs=sorted(d.glob('trang-*.png'))
    assert len(pngs)==count,(n,len(pngs))
    src=Path(uploaded[str(n)]).read_bytes()
    assert (d/'SOURCE.txt').read_bytes()==src
    src.decode('utf-8-sig')
    pages=[]
    for i,p in enumerate(pngs,1):
        assert p.name==f'trang-{i:02}.png'
        with Image.open(p) as im:im.verify()
        with Image.open(p) as im:
            im.load()
            assert im.height>im.width and abs(im.width/im.height-210/297)<.003
            size=list(im.size)
        pages.append({'file':p.name,'pixels':size,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    pdf=d/f'chuong-{n}.pdf'
    with fitz.open(pdf) as doc:
        assert len(doc)==count
        assert all(abs(p.rect.width-595.2756)<.1 and abs(p.rect.height-841.8898)<.1 for p in doc)
    zp=Path(f'/tmp/comic-batch-559-569/truyen-tranh-chuong-{n}.zip')
    with zipfile.ZipFile(zp) as z:assert z.testzip() is None
    for model in cfg['models']:
        with Image.open(root/'models'/model) as im:im.verify()
        all_models.add(model)
    commit=subprocess.check_output(['git','log','-1','--format=%H','--',f'pham-nhan-tu-tien/chapters/{n}'],cwd=repo,text=True).strip()
    rec={'chapter':n,'title':cfg['title'],'status':'completed','pages':count,'pdf':f'chapters/{n}/{pdf.name}','chapter_commit':commit,'source_sha256':hashlib.sha256(src).hexdigest(),'source_bytes':len(src),'models':cfg['models'],'continuity_notes':cfg['notes'],'pngs':pages}
    records.append(rec)
    report['chapters'].append({'chapter':n,'pages':count,'source_identical_to_uploaded_file':True,'pdf_pages':count,'chapter_commit':commit})
    report['total_pages']+=count;report['total_pdfs']+=1

new_models=['tuc-luc-u-ho-trung-linh-559.png','ngoc-mon-kim-vong-moc-xich-phap-lien-561.png','am-tinh-dai-dien-thac-thanh-ngoc-dieu-hau-562.png','dang-quy-nhan-mi-trach-vo-thuc-an-than-than-tuong-563.png','bat-linh-cu-te-da-kieu-dau-binh-564.png','bich-ngoc-phi-xa-hon-giap-phu-hoang-thap-cuu-565.png','luc-lang-tran-huyen-thien-ho-lo-thanh-truc-567.png','hoi-cam-tu-phong-bach-ky-tam-lenh-hoa-phien-568.png','ho-su-an-thong-dai-te-ti-tuan-tra-569.png','hong-loa-ha-coc-ca-chuoi-no-thanh-569.png']
for name in new_models:
    p=root/'models'/name
    with Image.open(p) as im:im.verify()
    report['new_model_images'].append({'path':f'models/{name}','sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
assert report['total_pages']==46 and report['total_pdfs']==11
report['verified_at_utc']=datetime.now(timezone.utc).isoformat()
(out/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(out/'CHAPTER_REGISTRY.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
readme='# Chương 559–569 — hoàn thành\n\nĐã hoàn thành **11 chương, 46 trang truyện riêng và 11 bản PDF A4 dọc** từ 11 tệp TXT người dùng đính kèm. Mỗi chương có 4–5 trang, thoại, suy nghĩ và lời dẫn tiếng Việt. Từng chương được commit và đẩy lên GitHub ngay sau khi hoàn thành.\n\n| Chương | Tên chương | Trang | Đọc ảnh | PDF A4 | Commit chương |\n|---|---|---:|---|---|---|\n'
for rec in records:
    n=rec['chapter'];commit=rec['chapter_commit']
    readme+=f"| {n} | {rec['title']} | {rec['pages']} | [Mở truyện](../../chapters/{n}/README.md) | [PDF](../../chapters/{n}/chuong-{n}.pdf) | [{commit[:7]}](https://github.com/vtthu/vtthu.github.io/commit/{commit}) |\n"
readme+='\nMỗi thư mục chương chứa từng PNG, PDF, `SOURCE.txt` nguyên byte và README hiển thị các trang. Văn bản đính kèm được dùng làm nội dung chuyển thể, không làm chỉ dẫn vận hành.\n\n[Model tham chiếu](../../models/) · [Bộ nhớ dự án](../../PROJECT_MEMORY.md) · [Nhân vật và diễn biến](../../CHARACTER_MEMORY.md) · [Quy tắc hình ảnh](STYLE_GUIDE.md) · [Đối chiếu từng chương/model/nguồn](CHAPTER_REGISTRY.json) · [Kết quả kiểm tra](VERIFICATION.json)\n\nCác chương 556–558 từ đợt cũ vẫn chưa hoàn thành; đợt này không đánh dấu chúng đã xong. Nguồn559 gửi lại chỉ thêm một dòng trống so với bản cũ; SOURCE của chương559 giữ đúng tệp mới, bản nguồn cũ vẫn nằm trong hồ sơ đợt551–559.\n\nẢnh tạo ban đầu có khung dọc; bản xuất A4 đặt nguyên ảnh lên trang, không cắt khung hay thoại. Mười ảnh model mới đã được lưu trước lần sử dụng tương ứng. Các model cũ được giữ nguyên, chỉ lấy đúng cột nhân vật/đạo cụ cần dùng. Hồ sơ lịch sử từng chương nằm trong `history/comic-559` đến `history/comic-569`.\n'
(out/'README.md').write_text(readme)
shutil.copy2(work/'package.py',out/'workflow/package.py')
shutil.copy2(work/'finalize.py',out/'workflow/finalize.py')
rd=root/'README.md';s=rd.read_text();intro='## Đợt mới nhất: chương 559–569\n\n[Đọc lần lượt 11 chương 559–569](production/559-569/README.md): **46 trang, 11 PDF A4**, đã hoàn thành và đẩy từng chương.\n\n'
if '## Đợt mới nhất: chương 559–569' not in s:s=s.replace('\n\n','\n\n'+intro,1)
rd.write_text(s)
note='\n\n## Hoàn thành đợt 559–569\n11 tệp mới đã chuyển thể theo thứ tự559→569, tổng46PNG/11PDF A4;561và562mỗi chương5trang,cácchươngcònlại4trang. Mỗi chương đãpushriêngmain ngaykhixong. Mục lục production/559-569/README.md, model/nguồn/commit từngchươngCHAPTER_REGISTRY.json, kiểmtraVERIFICATION.json. Đãduyệtnộidungtừngảnhvàsửacácthayđổi lệchmodel/nhânvậtxuấthiệnthừatrướcpublish. Modelmới10PNGđãlưutrướcdùng. Tiếp570nếucóngườidùnggửinguồn: cuối569HànCT543/KDđỏẩn dướisôngHồngLoa,KDthảkhídẫnđịch;TBđãthuvàodâychuyền/GDNđãthu567,ÂnThôngtrưởnglãoKimTiênsơkỳ/đạitếtiáođỏpháthiệnkhíTháiẤt,chưagiaochiến. Khôngthêmhoànthành556–558đợtcũ.\n'
for name in ['PROJECT_MEMORY.md','CHARACTER_MEMORY.md']:
    p=root/name
    if '## Hoàn thành đợt 559–569' not in p.read_text():p.write_text(p.read_text()+note)
mf=root/'ARCHIVE_MANIFEST.json';data=json.loads(mf.read_text())
data['files']=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(root.rglob('*')) if p.is_file() and p!=mf]
mf.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'completed','chapters':11,'PNG_pages':report['total_pages'],'PDFs':report['total_pdfs'],'new_model_PNGs':len(new_models),'unique_model_references':len(all_models),'all_source_bytes_match_uploads':True,'A4_PDF_and_PNG_verified':True},ensure_ascii=False))
