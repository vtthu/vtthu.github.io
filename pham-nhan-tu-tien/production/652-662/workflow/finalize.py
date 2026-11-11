from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,zipfile,shutil,re
from PIL import Image
import fitz

repo=Path('/tmp/comic-publish-652'); root=repo/'pham-nhan-tu-tien'
work=Path('/workspace/comic-batch-652-662'); out=root/'production/652-662'
out.mkdir(parents=True,exist_ok=True)
base='025eb94'
def git(*args): return subprocess.check_output(['git',*args],cwd=repo,text=True).strip()
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
uploads=json.loads((work/'sources.json').read_text()); records=[]
for n in range(652,663):
    cfg=json.loads((work/f'{n}.json').read_text()); d=root/f'chapters/{n}'
    pages=sorted(d.glob('trang-*.png')); assert len(pages)==4
    source=Path(uploads[str(n)]).read_bytes()
    assert source==(d/'SOURCE.txt').read_bytes()==(work/f'CHUONG {n}.txt').read_bytes()
    pngs=[]
    for i,p in enumerate(pages,1):
        assert p.name==f'trang-{i:02}.png'
        with Image.open(p) as im: im.verify()
        with Image.open(p) as im:
            im.load(); assert im.size==(1055,1492)
            assert abs(im.width/im.height-210/297)<.003
        pngs.append({'file':p.name,'pixels':[1055,1492],'sha256':digest(p)})
    with fitz.open(d/f'chuong-{n}.pdf') as doc:
        assert len(doc)==4
        assert all(abs(p.rect.width-595.2756)<.1 and abs(p.rect.height-841.8898)<.1 for p in doc)
    for m in cfg['models']:
        with Image.open(root/'models'/m) as im: im.verify()
    with zipfile.ZipFile(f'/tmp/comic-batch-652-662/truyen-tranh-chuong-{n}.zip') as z: assert z.testzip() is None
    commit=git('log','-1','--format=%H','--',f'pham-nhan-tu-tien/chapters/{n}')
    records.append({'chapter':n,'title':cfg['title'],'status':'completed','pages':4,'chapter_commit':commit,'source_bytes':len(source),'source_sha256':hashlib.sha256(source).hexdigest(),'models':cfg['models'],'continuity_notes':cfg['notes'],'pngs':pngs})

changed=git('diff','--name-only',base,'HEAD').splitlines()
assert all(p.startswith('pham-nhan-tu-tien/') for p in changed)
new=[p.split('/models/')[1] for p in changed if '/models/' in p]
for f in new:
    with Image.open(root/'models'/f) as im: im.verify()
report={'status':'completed','verified_at_utc':datetime.now(timezone.utc).isoformat(),'chapters':11,'PNG_pages':44,'PDFs_A4':11,'PNG_pixels':[1055,1492],'source_identical_to_user_uploads':True,'PDF_page_counts_and_A4_verified':True,'all_PNG_decodes_and_portrait_A4_verified':True,'ZIP_integrity_verified_locally':True,'root_website_untouched':True,'new_model_images':[{'path':'models/'+f,'sha256':digest(root/'models'/f)} for f in new]}
(out/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(out/'CHAPTER_REGISTRY.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
index='# Chương 652–662 — hoàn thành\n\n**11 chương · 44 trang PNG riêng · 11 PDF A4 dọc.** Chuyển thể lần lượt từ TXT người dùng đính kèm. Mỗi chương bốn trang nhiều khung, có thoại, suy nghĩ và lời dẫn tiếng Việt. Từng chương được commit và đẩy lên GitHub ngay khi hoàn thành.\n\n| Chương | Tên | Trang | Ảnh truyện | PDF | Commit |\n|---|---|---:|---|---|---|\n'
for r in records:
    n=r['chapter']; c=r['chapter_commit']
    index+=f"| {n} | {r['title']} | 4 | [Đọc truyện](../../chapters/{n}/README.md) | [PDF A4](../../chapters/{n}/chuong-{n}.pdf) | [{c[:7]}](https://github.com/vtthu/vtthu.github.io/commit/{c}) |\n"
continuity='Cuối662: Hàn CT603 áo teal rách, trâm ngọc xanh; Kim Tiên đỉnh phong, chưa giải Sát suy. Cùng Nhâm Hào DK653 áo lam giáp đen và Phong Lâm MP655 áo tím mạng trắng liên thủ đánh người cá trong hồ tầng ba Tam Thủy Tháp. Phong Lâm kích hoạt Cửu U Ma Đồng tinh điểm tím; chưa rõ lai lịch người cá. Nguyên Phong (Phong Khánh Nguyên PK634) đã chết, ô đỏ bị hủy. Người cá còn sống; khiên vuông lam, sáo lam đính lá trúc chưa ai lấy; thi thể đầu lớn nguyên vẹn, chưa rõ danh tính. Chưa xác nhận Quang Âm Chi Thủy. Hắc môn mở phóng hắc quang, Nhâm Hào dùng kiếm lớn lam, Han phóng đúng ba Thanh Trúc Phong Vân Kiếm; chưa có kết quả giao chiến. Thi Mị đã bị Ma Quang diệt661, MQ-HT588 hắc bào đã về trúc lâu tím Hoa Chi, tu vi Thái Ất ổn định theo656. Hồ Tam/Nhiệt Hỏa/Thạch Xuyên Không thất lạc sau655, không tự ghép về tổ đội. Tinh kỳ vàng thời gian Han cất hồ lô xanh; tinh kỳ bạc không gian TXK đã lấy. Không bổ sung diễn biến635–651.'
index+='\nMỗi chương có bốn PNG riêng, PDF A4, SOURCE.txt giữ nguyên byte và README hiển thị ảnh. Ảnh được đặt vừa trang A4, không cắt mất khung hoặc chữ.\n\n[Model tham chiếu](../../models/) · [Bộ nhớ dự án](../../PROJECT_MEMORY.md) · [Bộ nhớ nhân vật](../../CHARACTER_MEMORY.md) · [Nguồn và commit](CHAPTER_REGISTRY.json) · [Kiểm tra kỹ thuật](VERIFICATION.json) · [Quy tắc hình ảnh](STYLE_GUIDE.md)\n\nĐợt này chỉ xử lý652–662; không đánh dấu635–651 hoàn thành. Văn bản đính kèm được đọc như nội dung chuyển thể, không phải chỉ dẫn vận hành.\n\n'+continuity+'\n'
(out/'README.md').write_text(index)
style='''# Quy tắc hình ảnh 652–662

Mỗi chương4–5 trang A4 dọc; đợt này4 trang/chương. Một PNG là một trang. Phong cách tiên hiệp bán hiện thực3D, nhiều khung, thoại, suy nghĩ, lời dẫn tiếng Việt. Dùng PNG model trực tiếp, lưu model mới trước lần đầu xuất hiện. Nhãn tự phát trên model không thêm dữ kiện nguyên tác.

Hàn giữ CT603 trung niên sạch râu tóc đen trâm ngọc xanh áo TEAL trúc vàng, không ghi đè HL-01 V2. Tên Lệ Giang Lưu chỉ là bí danh. Kích hoạt Cửu U Ma Đồng mắt tím. Chưa tự nâng Thái Ất hoặc chữa Sát suy. Tay phải ngón trỏ và giữa trắng ngọc hoa bạc khắc chìm, không mọc hoa thật. Sau660 áo rách. Bảo Luân có mắt vàng lớn; không lấy giáp606 chỉ vì dùng bảng tham chiếu Bảo Luân.

Hồ Tam HT652 tóc đen râu nhỏ bạch bào; TXK652 tóc bạc áo tím; Nhiệt Hỏa NH603 già tóc râu trắng áo lam lửa. Xi Dung XD652 tóc đỏ sừng tê giác vòng tai vàng; Công Thâu Thiên CTT652 khác Công Thâu Cửu. Phong Khánh Nguyên PK634 nam trẻ áo choàng đỏ ô đỏ sẫm, bí danh Nguyên Phong; chết662. Đại kiếm sĩ DK653 tự giới thiệu Nhâm Hào658 (nguồn659 có biến thể Nhậm); giữ mặt vuông áo choàng lam giáp đen kiếm bản lớn, phát ánh lam662. Ma nữ MP655 tự xưng Phong Lâm658, áo tím tóc đen trâm hoa bạc mạng trắng che mũi miệng; mắt tím tinh điểm662, không tự gán danh tính khác. Ma Quang giữ MQ-HT588 mặt xám hắc bào; không dùng da đen MQ01.

Tinh kỳ vàng thời gian thuộc Han, bạc không gian thuộc TXK. Ngân Nguyệt 空 là hai mặt MỘT lệnh bài, không phải hai món. Sư tử đá TXK cao ba thước, không theo nhãn model tự ghi ba mét. Pháp tướng không phải nhân vật sống mới. Gậy/cung/giáp tạm không thay model mặt.

Thủy Diễn Cung là hải lam tinh thạch trên quảng trường, không dưới biển. Tam Thủy Tháp đúng ba tầng, tầng một bát giác, hỏa diễm là huyễn cảnh; tầng hai băng thật, Thi Mị là vật âm sát không máu đỏ; tầng ba thư phòng đổ nát và hồ nước. Tượng đầu lớn657 đổ khác tượng đỉnh núi659 đứng nguyên. Năm lối rẽ theo thứ tự Đệ Tử Bãi, Tam Thủy Tháp, Ngũ Linh Các, Thừa Thiên Điện, Thiên Dược Cốc.

Địa Hồn Yêu657–658 là quỷ vật lông đen sừng đỏ, trùm có huyết văn; cánh đỏ chỉ hiện658. Hạch đen cho MQ, không phải máu. Thi Mị ban đầu659 là bóng giống Han; lộ thật660 da lam tím mắt trắng áo rách. Sát thai bảy lỗ ở giao ngực bụng, không đầu/tim/đan điền; MQ diệt661. Đồng thi đầu lớn661 là thi thể hình đồng tử được bảo tồn, không đồng kim loại; thân dưới năm THƯỚC, nhãn trượng trên model sai. Cửa đen662 rộng tổng2–3trượng, không dùng nhãn mỗi cánh trên model. Người cá hai tay hai chân màng vảy lam, khôi lỗi vàng đúng tám tay, không tự gán lai lịch. Khiên vuông lam và sáo lam có7–8lá trúc chưa nhận chủ.
'''
(out/'STYLE_GUIDE.md').write_text(style)
(out/'workflow').mkdir(exist_ok=True)
for f in ['package.py','finalize.py']: shutil.copy2(work/f,out/'workflow'/f)
shutil.copy2(Path('/workspace/github-comic-backup/pham-nhan-tu-tien/production/603-613/workflow/image_result_save.js'),out/'workflow/image_result_save.js')
rd=root/'README.md'; s=rd.read_text(); s=re.sub(r'## Đợt mới nhất: chương ([^\n]+)',r'## Đợt chương \1',s)
s=s.replace('\n\n','\n\n## Đợt mới nhất: chương 652–662\n\n[Đọc lần lượt 11 chương](production/652-662/README.md): **44 trang PNG, 11 PDF A4**, đã đẩy từng chương.\n\n',1); rd.write_text(s)
note='\n\n## Hoàn thành đợt 652–662\n11 chương theo thứ tự, mỗi chương4 trang A4;44 PNG,11 PDF; commit/push riêng từng chương. Mục lục production/652-662/README.md. Không đánh dấu635–651 hoàn thành.\n\n'+style.split('\n',1)[1]+'\n'+continuity+'\n\nModel mới đã lưu trước dùng:\n'+'\n'.join('- models/'+f for f in new)+'\n'
for name in ['PROJECT_MEMORY.md','CHARACTER_MEMORY.md']:
    p=root/name
    if '## Hoàn thành đợt 652–662' not in p.read_text(): p.write_text(p.read_text()+note)
for p in [out/'README.md']+[root/f'chapters/{n}/README.md' for n in range(652,663)]:
    for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if not link.startswith(('https:','http:','#')): assert (p.parent/link).exists(),(p,link)
mf=root/'ARCHIVE_MANIFEST.json'; data=json.loads(mf.read_text())
old=json.loads(git('show',base+':pham-nhan-tu-tien/ARCHIVE_MANIFEST.json'))
oldpaths={x['path'] for x in old['files']}; entries={x['path']:x for x in data['files']}
assert oldpaths.issubset(entries)
for p in sorted(root.rglob('*')):
    if p.is_file() and p!=mf:
        rel=str(p.relative_to(root)); entries[rel]={'path':rel,'bytes':p.stat().st_size,'sha256':digest(p)}
data['files']=[entries[k] for k in sorted(entries)]
mf.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))

